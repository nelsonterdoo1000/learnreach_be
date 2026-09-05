from django.urls import path
from rest_framework_simplejwt.views import TokenObtainPairView, TokenRefreshView
from . import views

urlpatterns = [
    # Auth Endpoints
    path('token/', TokenObtainPairView.as_view(), name='token_obtain_pair'),
    path('token/refresh/', TokenRefreshView.as_view(), name='token_refresh'),
    path('register/', views.register_user, name='register_user'),
    path('verify-signup/', views.verify_signup_otp, name='verify_signup_otp'),
    path('forgot-password-request/', views.forgot_password_request, name='forgot_password_request'),
    path('forgot-password-reset/', views.forgot_password_reset, name='forgot_password_reset'),
    
    # WhatsApp Webhook
    path('webhook/whatsapp/', views.whatsapp_webhook, name='whatsapp_webhook'),
    
    # React App Endpoints
    path('sessions/', views.get_user_sessions, name='get_user_sessions'),
    path('sessions/<int:session_id>/messages/', views.get_session_messages, name='get_session_messages'),
    path('sessions/<int:session_id>/analyze/', views.analyze_session_view, name='analyze_session_view'),
    path('sessions/<int:session_id>/flashcards/', views.generate_flashcards_view, name='generate_flashcards_view'),
    path('chat/', views.web_chat_message, name='web_chat_message'),
    path('email-chat/', views.email_chat_history, name='email_chat_history'),
    path('quiz/generate/', views.generate_quiz_view, name='generate_quiz'),
    path('upload-material/', views.upload_material, name='upload_material'),
    
    # AI Weekend Endpoints
    path('ai-weekend/verify-payment/', views.ai_weekend_verify_payment, name='ai_weekend_verify_payment'),
    path('ai-weekend/checkout-intent/', views.log_checkout_intent, name='log_checkout_intent'),
    path('ai-weekend/paystack-webhook/', views.paystack_webhook, name='paystack_webhook'),
]

