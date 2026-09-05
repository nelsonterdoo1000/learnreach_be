from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.response import Response
from rest_framework import status
from django.contrib.auth.models import User
from django.utils.crypto import get_random_string
from .models import Profile, LearningSession, Message, Quiz, Question, Answer, OTP
from .ai_utils import generate_explanation, generate_quiz, analyze_session, generate_flashcards
from .email_utils import send_signup_otp, send_reset_otp, send_chat_transcript, send_welcome_email
import PyPDF2
import urllib.parse
import markdown

@api_view(['POST'])
@permission_classes([AllowAny]) # Webhooks need to be publicly accessible, but ideally validated by a signature
def whatsapp_webhook(request):
    """
    Webhook endpoint to receive incoming WhatsApp messages (e.g. from Twilio).
    Twilio sends form-encoded data.
    """
    # Twilio sends data as form variables
    sender = request.POST.get('From', '')
    incoming_msg = request.POST.get('Body', '').strip()
    
    if not sender or not incoming_msg:
        return Response({'error': 'Invalid request'}, status=status.HTTP_400_BAD_REQUEST)
    
    # In a real application, we would map the phone number (sender) to a User Profile.
    # For this prototype, we can use a mock user or create one on the fly.
    user, created = User.objects.get_or_create(username=sender, defaults={'password': 'unusable_password'})
    profile, _ = Profile.objects.get_or_create(user=user, defaults={'role': 'learner', 'learning_level': 'High School'})
    
    # Find or create an active LearningSession for this user
    session = LearningSession.objects.filter(learner=user).order_by('-started_at').first()
    if not session:
        session = LearningSession.objects.create(learner=user, custom_topic=incoming_msg)
    
    # Save user message
    Message.objects.create(session=session, sender='user', content=incoming_msg)
    
    # Generate AI explanation based on the incoming message acting as a topic or question
    ai_response_text = generate_explanation(incoming_msg, profile.learning_level)
    
    # Save AI response
    Message.objects.create(session=session, sender='ai', content=ai_response_text)
    
    # Return TwiML response (Twilio XML format) for the WhatsApp reply
    from twilio.twiml.messaging_response import MessagingResponse
    resp = MessagingResponse()
    resp.message(ai_response_text)
    
    # Twilio expects an XML response with Content-Type: text/xml
    from django.http import HttpResponse
    return HttpResponse(str(resp), content_type='text/xml')

@api_view(['GET'])
@permission_classes([IsAuthenticated])
def get_user_sessions(request):
    """
    Fetch all learning sessions for the currently authenticated web user.
    """
    sessions = LearningSession.objects.filter(learner=request.user).order_by('-started_at')
    # Serialize data manually for prototype speed, or use serializers.ModelSerializer
    data = []
    for s in sessions:
        topic_name = s.topic.name if s.topic else s.custom_topic
        data.append({
            'id': s.id,
            'topic': topic_name,
            'started_at': s.started_at,
            'summary': s.summary,
            'learning_gaps': s.learning_gaps,
            'recommendations': s.recommendations
        })
    return Response(data)

@api_view(['GET'])
@permission_classes([IsAuthenticated])
def get_session_messages(request, session_id):
    """
    Fetch all messages for a specific session for the authenticated user.
    """
    try:
        session = LearningSession.objects.get(id=session_id, learner=request.user)
    except LearningSession.DoesNotExist:
        return Response({'error': 'Session not found'}, status=status.HTTP_404_NOT_FOUND)
        
    messages = Message.objects.filter(session=session).order_by('timestamp')
    data = []
    for m in messages:
        data.append({
            'sender': m.sender,
            'text': m.content,
            'timestamp': m.timestamp
        })
        
    return Response(data)

@api_view(['POST'])
@permission_classes([IsAuthenticated])
def analyze_session_view(request, session_id):
    """
    Trigger AI analysis of a specific session to generate summary and learning gaps.
    """
    try:
        session = LearningSession.objects.get(id=session_id)
    except LearningSession.DoesNotExist:
        return Response({'error': 'Session not found'}, status=status.HTTP_404_NOT_FOUND)
        
    messages = Message.objects.filter(session=session).order_by('timestamp')
    if not messages:
        return Response({'error': 'No messages to analyze'}, status=status.HTTP_400_BAD_REQUEST)
        
    chat_history = [{'sender': m.sender, 'text': m.content} for m in messages]
    
    analysis = analyze_session(chat_history)
    if not analysis:
        return Response({'error': 'Failed to generate analysis'}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
        
    session.summary = analysis.get('summary', '')
    session.learning_gaps = analysis.get('learning_gaps', '')
    session.recommendations = analysis.get('recommendations', '')
    session.save()
    
    return Response({
        'summary': session.summary,
        'learning_gaps': session.learning_gaps,
        'recommendations': session.recommendations
    })

@api_view(['POST'])
@permission_classes([IsAuthenticated])
def web_chat_message(request):
    """
    Endpoint for the React frontend to send a message to the AI.
    """
    session_id = request.data.get('session_id')
    content = request.data.get('content')
    language = request.data.get('language', 'English')
    
    if not content:
        return Response({'error': 'Content is required'}, status=status.HTTP_400_BAD_REQUEST)
        
    try:
        if session_id:
            session = LearningSession.objects.get(id=session_id, learner=request.user)
        else:
            session = LearningSession.objects.create(learner=request.user, custom_topic=content)
    except LearningSession.DoesNotExist:
        return Response({'error': 'Session not found'}, status=status.HTTP_404_NOT_FOUND)
        
    Message.objects.create(session=session, sender='user', content=content)
    
    # Generate AI response
    profile = Profile.objects.get(user=request.user)
    ai_response_text = generate_explanation(content, profile.learning_level, file_context=session.file_context, language=language)
    
    Message.objects.create(session=session, sender='ai', content=ai_response_text)
    
    return Response({
        'session_id': session.id,
        'user_message': content,
        'ai_response': ai_response_text
    })

@api_view(['POST'])
@permission_classes([IsAuthenticated])
def generate_flashcards_view(request, session_id):
    """
    Endpoint for React frontend to generate flashcards based on learning gaps.
    """
    language = request.data.get('language', 'English')
    
    try:
        session = LearningSession.objects.get(id=session_id, learner=request.user)
    except LearningSession.DoesNotExist:
        return Response({'error': 'Session not found'}, status=status.HTTP_404_NOT_FOUND)
        
    messages = Message.objects.filter(session=session).order_by('timestamp')
    chat_history = ""
    for m in messages:
        sender_name = "Learner" if m.sender == 'user' else "AI Tutor"
        chat_history += f"[{sender_name}]: {m.content}\n"
        
    # Generate flashcards data from Gemini
    flashcards_data = generate_flashcards(chat_history, file_context=session.file_context, language=language)
    
    if not flashcards_data:
        return Response({'error': 'Failed to generate flashcards'}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
        
    return Response({
        'session_id': session.id,
        'flashcards': flashcards_data
    })

@api_view(['POST'])
@permission_classes([IsAuthenticated])
def generate_quiz_view(request):
    """
    Endpoint for React frontend to generate a quiz for a specific topic.
    """
    session_id = request.data.get('session_id')
    topic = request.data.get('topic')
    num_questions = int(request.data.get('num_questions', 3))
    
    if not topic or not session_id:
        return Response({'error': 'Topic and session_id are required'}, status=status.HTTP_400_BAD_REQUEST)
        
    try:
        session = LearningSession.objects.get(id=session_id, learner=request.user)
    except LearningSession.DoesNotExist:
        return Response({'error': 'Session not found'}, status=status.HTTP_404_NOT_FOUND)
        
    profile = Profile.objects.get(user=request.user)
    
    # Get context for the quiz
    messages = Message.objects.filter(session=session).order_by('timestamp')
    chat_history = ""
    for m in messages:
        sender_name = "Learner" if m.sender == 'user' else "AI Tutor"
        chat_history += f"[{sender_name}]: {m.content}\n"
    
    # Generate quiz data from Gemini
    quiz_data = generate_quiz(topic, profile.learning_level, num_questions=num_questions, chat_history=chat_history, file_context=session.file_context)
    
    if not quiz_data:
        return Response({'error': 'Failed to generate quiz'}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
        
    # Save to database
    quiz = Quiz.objects.create(session=session, total_questions=len(quiz_data))
    
    for q_data in quiz_data:
        Question.objects.create(
            quiz=quiz,
            text=q_data.get('text', ''),
            options=q_data.get('options', []),
            correct_answer=q_data.get('correct_answer', ''),
            explanation=q_data.get('explanation', '')
        )
        
    return Response({
        'quiz_id': quiz.id,
        'questions': quiz_data
    })

@api_view(['POST'])
@permission_classes([AllowAny])
def register_user(request):
    email = request.data.get('email')
    password = request.data.get('password')
    
    if not email or not password:
        return Response({'error': 'Email and password are required'}, status=status.HTTP_400_BAD_REQUEST)
        
    if User.objects.filter(username=email).exists():
        return Response({'error': 'Email already exists'}, status=status.HTTP_400_BAD_REQUEST)
        
    user = User.objects.create_user(username=email, email=email, password=password)
    user.is_active = False # Require OTP verification
    user.save()
    
    Profile.objects.create(user=user, role='learner', learning_level='High School')
    
    # Generate and send OTP
    code = get_random_string(length=6, allowed_chars='0123456789')
    OTP.objects.create(user=user, code=code, purpose='signup')
    send_signup_otp(email, code)
    
    return Response({'message': 'OTP sent to email. Please verify.'}, status=status.HTTP_201_CREATED)

@api_view(['POST'])
@permission_classes([AllowAny])
def verify_signup_otp(request):
    email = request.data.get('email')
    code = request.data.get('code')
    
    try:
        user = User.objects.get(username=email)
        otp = OTP.objects.get(user=user, code=code, purpose='signup')
        
        user.is_active = True
        user.save()
        otp.delete()
        
        send_welcome_email(user.email)
        
        return Response({'message': 'Account verified successfully'})
    except (User.DoesNotExist, OTP.DoesNotExist):
        return Response({'error': 'Invalid email or OTP'}, status=status.HTTP_400_BAD_REQUEST)

@api_view(['POST'])
@permission_classes([AllowAny])
def forgot_password_request(request):
    email = request.data.get('email')
    try:
        user = User.objects.get(username=email)
        # Clear old reset OTPs
        OTP.objects.filter(user=user, purpose='reset').delete()
        
        code = get_random_string(length=6, allowed_chars='0123456789')
        OTP.objects.create(user=user, code=code, purpose='reset')
        send_reset_otp(email, code)
        
        return Response({'message': 'Reset OTP sent to email'})
    except User.DoesNotExist:
        # Return success anyway to prevent email enumeration
        return Response({'message': 'Reset OTP sent to email'})

@api_view(['POST'])
@permission_classes([AllowAny])
def forgot_password_reset(request):
    email = request.data.get('email')
    code = request.data.get('code')
    new_password = request.data.get('new_password')
    
    try:
        user = User.objects.get(username=email)
        otp = OTP.objects.get(user=user, code=code, purpose='reset')
        
        user.set_password(new_password)
        user.save()
        otp.delete()
        
        return Response({'message': 'Password reset successfully'})
    except (User.DoesNotExist, OTP.DoesNotExist):
        return Response({'error': 'Invalid email or OTP'}, status=status.HTTP_400_BAD_REQUEST)

@api_view(['POST'])
@permission_classes([IsAuthenticated])
def email_chat_history(request):
    session_id = request.data.get('session_id')
    try:
        session = LearningSession.objects.get(id=session_id, learner=request.user)
    except LearningSession.DoesNotExist:
        return Response({'error': 'Session not found'}, status=status.HTTP_404_NOT_FOUND)
        
    messages = Message.objects.filter(session=session).order_by('timestamp')
    if not messages:
        return Response({'error': 'No messages in this session'}, status=status.HTTP_400_BAD_REQUEST)
        
    transcript_html = ""
    for m in messages:
        sender_name = "You" if m.sender == 'user' else "AI Tutor"
        color = "#000000" if m.sender == 'user' else "#2e7d32"
        html_content = markdown.markdown(m.content, extensions=['extra', 'nl2br'])
        transcript_html += f"<div style='color: {color}; margin-bottom: 12px;'><strong>[{sender_name}]:</strong> {html_content}</div>"
        
    success = send_chat_transcript(request.user.email, transcript_html)
    if success:
        return Response({'message': 'Chat transcript emailed successfully'})
    return Response({'error': 'Failed to send email'}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

@api_view(['POST'])
def upload_material(request):
    session_id = request.data.get('session_id')
    pdf_file = request.FILES.get('file')
    
    if not session_id or not pdf_file:
        return Response({'error': 'session_id and file are required'}, status=status.HTTP_400_BAD_REQUEST)
        
    try:
        session = LearningSession.objects.get(id=session_id, learner=request.user)
    except LearningSession.DoesNotExist:
        return Response({'error': 'Session not found'}, status=status.HTTP_404_NOT_FOUND)
        
    try:
        pdf_reader = PyPDF2.PdfReader(pdf_file)
        text = ""
        for page in pdf_reader.pages:
            text += page.extract_text() + "\n"
            
        session.file_context = text
        session.save()
        return Response({'message': 'Material uploaded and processed successfully'})
    except Exception as e:
        return Response({'error': f'Failed to process PDF: {str(e)}'}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

from .models import AIWeekendRegistration, AIWeekendLead
from .email_utils import send_ai_weekend_locked_in, send_ai_weekend_access_details, send_abandoned_cart_email

@api_view(['POST'])
@permission_classes([AllowAny])
def log_checkout_intent(request):
    email = request.data.get('email')
    name = request.data.get('name')
    phone = request.data.get('phone', '')

    if not email or not name:
        return Response({'error': 'Name and email are required'}, status=status.HTTP_400_BAD_REQUEST)

    email = email.strip().lower()

    lead, created = AIWeekendLead.objects.get_or_create(email=email, defaults={'name': name, 'phone': phone})
    if not created:
        lead.name = name
        lead.phone = phone
        # If user hasn't paid yet, reset timer so abandoned cart reminder triggers 10 mins after this attempt
        if not AIWeekendRegistration.objects.filter(email=email, is_paid=True).exists():
            from django.utils import timezone
            lead.created_at = timezone.now()
            lead.email_1_sent = False
            lead.email_2_sent = False
            lead.email_3_sent = False
        lead.save()

    return Response({'message': 'Checkout intent logged'}, status=status.HTTP_200_OK)


@api_view(['POST'])
@permission_classes([AllowAny])
def ai_weekend_verify_payment(request):
    """
    Endpoint for frontend to verify Paystack payment for AI Weekend.
    """
    reference = request.data.get('reference')
    email = request.data.get('email')
    name = request.data.get('name')
    phone = request.data.get('phone', '')

    if not reference or not email or not name:
        return Response({'error': 'Reference, email, and name are required'}, status=status.HTTP_400_BAD_REQUEST)

    email = email.strip().lower()

    # Find existing registration by email or reference, or create a new one
    reg = AIWeekendRegistration.objects.filter(payment_reference=reference).first()
    if not reg:
        reg = AIWeekendRegistration.objects.filter(email=email).first()

    if reg:
        reg.is_paid = True
        reg.name = name or reg.name
        reg.phone = phone or reg.phone
        reg.payment_reference = reference
        reg.save()
    else:
        reg = AIWeekendRegistration.objects.create(
            name=name,
            email=email,
            phone=phone,
            payment_reference=reference,
            is_paid=True
        )

    # Send confirmation & onboarding emails
    try:
        send_ai_weekend_locked_in(email)
    except Exception as e:
        print(f"Failed to send locked-in email to {email}: {e}")

    try:
        if not reg.access_email_sent:
            send_ai_weekend_access_details(email)
            reg.access_email_sent = True
            reg.save()
    except Exception as e:
        print(f"Failed to send access details email to {email}: {e}")

    return Response({'message': 'Payment verified and registration complete', 'id': reg.id}, status=status.HTTP_200_OK)


import hmac
import hashlib
import json
import os
from django.views.decorators.csrf import csrf_exempt

@csrf_exempt
@api_view(['POST'])
@permission_classes([AllowAny])
def paystack_webhook(request):
    """
    Paystack Webhook listener.
    Automatically catches 'charge.success' events server-to-server even if the user
    closed their browser before the frontend callback could fire.
    """
    secret = os.getenv('PAYSTACK_SECRET', '').strip()
    
    # Signature verification if secret key is present
    signature = request.headers.get('x-paystack-signature')
    if secret and signature:
        computed_hash = hmac.new(
            secret.encode('utf-8'),
            request.body,
            hashlib.sha512
        ).hexdigest()
        if computed_hash != signature:
            return Response({'error': 'Invalid signature'}, status=status.HTTP_400_BAD_REQUEST)
    
    try:
        payload = json.loads(request.body.decode('utf-8'))
    except Exception:
        return Response({'error': 'Invalid JSON'}, status=status.HTTP_400_BAD_REQUEST)
        
    event = payload.get('event')
    if event == 'charge.success':
        data = payload.get('data', {})
        reference = data.get('reference')
        customer = data.get('customer', {})
        email = (customer.get('email') or '').strip().lower()
        metadata = data.get('metadata', {})
        
        name = ''
        phone = customer.get('phone', '') or ''
        
        # Extract name/phone from metadata if passed by Paystack
        if isinstance(metadata, dict):
            name = metadata.get('name') or metadata.get('full_name') or ''
            phone = phone or metadata.get('phone', '')
            custom_fields = metadata.get('custom_fields', [])
            if isinstance(custom_fields, list):
                for field in custom_fields:
                    if field.get('variable_name') in ['name', 'full_name'] and not name:
                        name = field.get('value', '')
                    if field.get('variable_name') in ['phone', 'phone_number'] and not phone:
                        phone = field.get('value', '')

        if not name:
            name = f"{customer.get('first_name', '')} {customer.get('last_name', '')}".strip()
            
        # Fallback to AIWeekendLead if name/phone missing
        lead = AIWeekendLead.objects.filter(email=email).first()
        if lead:
            name = name or lead.name
            phone = phone or lead.phone

        if email:
            reg = AIWeekendRegistration.objects.filter(payment_reference=reference).first()
            if not reg:
                reg = AIWeekendRegistration.objects.filter(email=email).first()

            if reg:
                reg.is_paid = True
                if reference and not reg.payment_reference:
                    reg.payment_reference = reference
                if name and (not reg.name or reg.name == 'Participant'):
                    reg.name = name
                if phone and not reg.phone:
                    reg.phone = phone
                reg.save()
            else:
                reg = AIWeekendRegistration.objects.create(
                    name=name or 'Participant',
                    email=email,
                    phone=phone,
                    payment_reference=reference,
                    is_paid=True
                )
            
            # Fire both onboarding emails immediately
            try:
                send_ai_weekend_locked_in(email)
            except Exception as e:
                print(f"Webhook locked-in email error for {email}: {e}")

            try:
                if not reg.access_email_sent:
                    send_ai_weekend_access_details(email)
                    reg.access_email_sent = True
                    reg.save()
            except Exception as e:
                print(f"Webhook access details email error for {email}: {e}")

    return Response({'status': 'success'}, status=status.HTTP_200_OK)

