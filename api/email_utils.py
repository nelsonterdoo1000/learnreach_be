import requests
import json
import os
from django.conf import settings

ZEPTOMAIL_URL = "https://api.zeptomail.com/v1.1/email"

ZEPTOMAIL_SEND_TOKEN = os.environ.get("ZEPTOMAIL_SEND_TOKEN", "wSsVR60krEX5B6p7zmesJ7s9nV5RVFmlQRss0Qf07SD5T/7C98c/wkOcVw+mFPkbRW5uRjpHo7wskRxV22YKitwvygoBACiF9mqRe1U4J3x17qnvhDzPWG1blxWPL40AxQtpn2JmFskk+g==")
SENDER_ADDRESS = "noreply@careerdevnetwork.com"
SENDER_NAME = "Nelson"

def send_zeptomail(to_email, subject, html_body):
    """
    Sends an email using the ZeptoMail REST API.
    If no token is provided, it simply prints to the terminal for local testing.
    """
    if not ZEPTOMAIL_SEND_TOKEN:
        print(f"\n[MOCK EMAIL SENT TO {to_email}]")
        print(f"Subject: {subject}")
        print(f"Body: {html_body}")
        print("-" * 40 + "\n")
        return True
        
    headers = {
        "Accept": "application/json",
        "Content-Type": "application/json",
        "Authorization": f"Zoho-enczapikey {ZEPTOMAIL_SEND_TOKEN}"
    }
    
    payload = {
        "from": {
            "address": SENDER_ADDRESS,
            "name": SENDER_NAME
        },
        "to": [
            {
                "email_address": {
                    "address": to_email,
                }
            }
        ],
        "subject": subject,
        "htmlbody": html_body,
    }
    
    try:
        response = requests.post(ZEPTOMAIL_URL, headers=headers, data=json.dumps(payload))
        if response.status_code in [200, 201]:
            return True
        print(f"ZeptoMail Error: {response.text}")
        return False
    except Exception as e:
        print(f"Failed to send email: {e}")
        return False

def get_base_html(title, content, app_name="LearnReach", footer_text="&copy; 2026 LearnReach. All rights reserved."):
    return f"""
    <!DOCTYPE html>
    <html>
    <head>
        <meta charset="utf-8">
        <meta name="viewport" content="width=device-width, initial-scale=1.0">
    </head>
    <body style="font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif; background-color: #f4f7f6; margin: 0; padding: 40px 20px;">
        <div style="max-width: 600px; margin: 0 auto; background-color: #ffffff; border-radius: 12px; overflow: hidden; box-shadow: 0 4px 15px rgba(0,0,0,0.05);">
            <div style="background-color: #1a1a1a; padding: 30px; text-align: center;">
                <h1 style="color: #ffffff; margin: 0; font-size: 28px; font-weight: 600; letter-spacing: 1px;">{app_name}</h1>
            </div>
            <div style="padding: 40px 30px;">
                <h2 style="color: #1a1a1a; margin-top: 0; margin-bottom: 24px; font-size: 22px;">{title}</h2>
                <div style="color: #4a5568; font-size: 16px; line-height: 1.6;">
                    {content}
                </div>
            </div>
            <div style="background-color: #f8fafc; padding: 20px; text-align: center; border-top: 1px solid #edf2f7;">
                <p style="margin: 0; color: #718096; font-size: 14px;">{footer_text}</p>
                <p style="margin: 5px 0 0; color: #a0aec0; font-size: 12px;">This is an automated message, please do not reply.</p>
            </div>
        </div>
    </body>
    </html>
    """

def send_signup_otp(email, code):
    subject = "Verify your LearnReach Account"
    content = f"""
        <p>Welcome to LearnReach!</p>
        <p>To complete your registration, please use the following verification code:</p>
        <div style="text-align: center; margin: 30px 0;">
            <span style="display: inline-block; padding: 15px 30px; background-color: #f0fdf4; color: #166534; font-size: 32px; font-weight: bold; letter-spacing: 8px; border-radius: 8px; border: 2px dashed #bbf7d0;">{code}</span>
        </div>
        <p>This code will expire shortly. If you did not request this email, please ignore it.</p>
    """
    html_body = get_base_html("Account Verification", content)
    return send_zeptomail(email, subject, html_body)

def send_reset_otp(email, code):
    subject = "Reset your LearnReach Password"
    content = f"""
        <p>We received a request to reset your password.</p>
        <p>Use the following code to set up a new password:</p>
        <div style="text-align: center; margin: 30px 0;">
            <span style="display: inline-block; padding: 15px 30px; background-color: #f0fdf4; color: #166534; font-size: 32px; font-weight: bold; letter-spacing: 8px; border-radius: 8px; border: 2px dashed #bbf7d0;">{code}</span>
        </div>
        <p>If you did not request a password reset, you can safely ignore this email. Your password will remain unchanged.</p>
    """
    html_body = get_base_html("Password Reset Request", content)
    return send_zeptomail(email, subject, html_body)

def send_chat_transcript(email, transcript_html):
    subject = "Your LearnReach AI Session Transcript"
    content = f"""
        <p>Here is a copy of your recent conversation with your AI Tutor.</p>
        <div style="margin-top: 24px; padding: 20px; background-color: #f8fafc; border-radius: 8px; border: 1px solid #e2e8f0; max-height: 800px; overflow-y: auto;">
            {transcript_html}
        </div>
        <p style="margin-top: 24px;">Happy learning!</p>
    """
    html_body = get_base_html("Session Transcript", content)
    return send_zeptomail(email, subject, html_body)

def send_welcome_email(email):
    subject = "Welcome to LearnReach 2.0! 🚀"
    content = f"""
        <div style="background: linear-gradient(135deg, #e0f2fe 0%, #dcfce7 100%); padding: 30px; border-radius: 12px; margin-bottom: 24px;">
            <h2 style="color: #047857; margin-top: 0; font-size: 24px;">Your AI Tutor Awaits!</h2>
            <p style="color: #1f2937; font-size: 16px; margin-bottom: 0;">We're thrilled to have you on board. LearnReach is designed to break down complex topics, adapt to your learning speed, and help you master any subject.</p>
        </div>
        
        <h3 style="color: #1a1a1a; font-size: 20px; border-bottom: 2px solid #e5e7eb; padding-bottom: 8px;">Here's how to get the most out of it:</h3>
        
        <ul style="list-style-type: none; padding-left: 0; margin-top: 20px;">
            <li style="margin-bottom: 16px; display: flex; align-items: flex-start;">
                <span style="background-color: #dbeafe; color: #1e40af; border-radius: 50%; width: 28px; height: 28px; display: inline-flex; align-items: center; justify-content: center; margin-right: 12px; flex-shrink: 0; font-weight: bold;">1</span>
                <div>
                    <strong style="color: #1e3a8a; display: block; margin-bottom: 4px;">Chat & Learn</strong>
                    <span style="color: #4b5563;">Ask any question, or upload your PDF study materials. Your AI tutor will explain concepts simply using relatable analogies.</span>
                </div>
            </li>
            <li style="margin-bottom: 16px; display: flex; align-items: flex-start;">
                <span style="background-color: #fef3c7; color: #92400e; border-radius: 50%; width: 28px; height: 28px; display: inline-flex; align-items: center; justify-content: center; margin-right: 12px; flex-shrink: 0; font-weight: bold;">2</span>
                <div>
                    <strong style="color: #78350f; display: block; margin-bottom: 4px;">Speak & Listen</strong>
                    <span style="color: #4b5563;">Use the microphone to speak your questions, and hear the explanations out loud.</span>
                </div>
            </li>
            <li style="margin-bottom: 16px; display: flex; align-items: flex-start;">
                <span style="background-color: #f3e8ff; color: #6b21a8; border-radius: 50%; width: 28px; height: 28px; display: inline-flex; align-items: center; justify-content: center; margin-right: 12px; flex-shrink: 0; font-weight: bold;">3</span>
                <div>
                    <strong style="color: #581c87; display: block; margin-bottom: 4px;">Practice Quizzes</strong>
                    <span style="color: #4b5563;">Ask the tutor to generate a quiz to test your knowledge and get immediate feedback.</span>
                </div>
            </li>
        </ul>
        
        <div style="text-align: center; margin-top: 32px;">
            <a href="https://careerdevnetwork.com/login" style="display: inline-block; background-color: #0f6b4d; color: white; text-decoration: none; padding: 14px 28px; border-radius: 50px; font-weight: bold; font-size: 16px; box-shadow: 0 4px 12px rgba(15, 107, 77, 0.3);">Go to your Study Space →</a>
        </div>
    """
    html_body = get_base_html("Welcome to LearnReach!", content)
    return send_zeptomail(email, subject, html_body)

def send_ai_weekend_locked_in(email):
    subject = "Locked-In for the AI-Weekend Masterclass"
    content = """
        <div style="background: linear-gradient(135deg, #111 0%, #0a0a0a 100%); padding: 30px; border-radius: 12px; margin-bottom: 24px; color: #fff;">
            <h2 style="color: #00ff00; margin-top: 0; font-size: 24px;">You are Locked In! 🚀</h2>
            <p style="font-size: 16px; margin-bottom: 0;">Congratulations on securing your seat for the AI-Weekend Masterclass. Your 11:47pm moment is officially in motion.</p>
        </div>
        <p>In about 10 minutes, you will receive another email with your exclusive access details, the curriculum we will cover, and the tools you need to prepare.</p>
        <p>Get ready to build.</p>
        <p>- Terdoo Nelson Nondo</p>
    """
    html_body = get_base_html("Registration Confirmed", content, app_name="AI Weekend", footer_text="&copy; 2026 Career Dev Network. All rights reserved.")
    return send_zeptomail(email, subject, html_body)

def send_ai_weekend_access_details(email):
    subject = "AI-Weekend Access Details"
    content = """
        <div style="background: linear-gradient(135deg, #111 0%, #0a0a0a 100%); padding: 30px; border-radius: 12px; margin-bottom: 24px; color: #fff;">
            <h2 style="color: #00ff00; margin-top: 0; font-size: 24px;">Your Access Details</h2>
            <p style="font-size: 16px; margin-bottom: 0;">Here is everything you need for the AI-Weekend Masterclass on Sept 19th & 20th, 2026 (8PM - 11PM Daily).</p>
        </div>
        
        <h3 style="color: #1a1a1a; font-size: 20px; border-bottom: 2px solid #e5e7eb; padding-bottom: 8px;">Curriculum</h3>
        <ul>
            <li><strong>The Profit Centers:</strong> Discover actual digital products you can conceive, build, and list before Sunday night.</li>
            <li><strong>The Attention System:</strong> Learn how to use AI-powered ads to put your product directly in front of buyers.</li>
            <li><strong>The Automation Layer:</strong> Build the system that takes a total stranger from "never heard of you" to "money in your account" completely hands-free.</li>
        </ul>
        
        <h3 style="color: #1a1a1a; font-size: 20px; border-bottom: 2px solid #e5e7eb; padding-bottom: 8px;">Tools Needed</h3>
        <ul>
            <li>A laptop or desktop computer with a stable internet connection.</li>
            <li>Google Chrome browser.</li>
            <li>A free ChatGPT account.</li>
            <li>Your full attention.</li>
        </ul>

        <div style="background-color: #f0fdf4; border: 1px solid #bbf7d0; border-radius: 8px; padding: 18px; margin-top: 15px;">
            <p style="margin: 0 0 8px 0; color: #166534; font-weight: bold; font-size: 15px;">💡 Optional: Build Along With Me via Abacus AI ($10)</p>
            <p style="margin: 0 0 10px 0; color: #374151; font-size: 14px; line-height: 1.5;">
                If you want to build along with me live on screen as I build, you can optionally sign up for 
                <a href="https://chatllm.abacus.ai/GfBKHBRnfN" style="color: #0f6b4d; font-weight: bold; text-decoration: underline;">Abacus AI using this link</a>.
            </p>
            <p style="margin: 0; color: #4b5563; font-size: 13px; line-height: 1.5;">
                This will give you access to top-tier AI models like <strong>Claude</strong>, <strong>ChatGPT</strong>, <strong>Nano Banana</strong>, and <strong>Kimi</strong> for a fraction of the original cost of each individual model ($10).
            </p>
        </div>
    """
    html_body = get_base_html("Access Details", content, app_name="AI Weekend", footer_text="&copy; 2026 Career Dev Network. All rights reserved.")
    return send_zeptomail(email, subject, html_body)


def send_ai_weekend_meeting_link(email):
    subject = "AI-Weekend Meeting Link - Starting Tomorrow"
    content = """
        <div style="background: linear-gradient(135deg, #111 0%, #0a0a0a 100%); padding: 30px; border-radius: 12px; margin-bottom: 24px; color: #fff;">
            <h2 style="color: #00ff00; margin-top: 0; font-size: 24px;">AI-Weekend Masterclass Link</h2>
            <p style="font-size: 16px; margin-bottom: 0;">We are starting soon! Here is your meeting link and everything you need to prepare for the AI-Weekend Masterclass on Sept 19th & 20th, 2026 (8PM - 11PM Daily).</p>
        </div>
        
        <h3 style="color: #1a1a1a; font-size: 20px; border-bottom: 2px solid #e5e7eb; padding-bottom: 8px;">Meeting Link</h3>
        <p><strong>Join here:</strong> <a href="https://meet.google.com/pen-zpft-ppu" style="color: #2e7d32; font-weight: bold;">https://meet.google.com/pen-zpft-ppu</a></p>
        
        <h3 style="color: #1a1a1a; font-size: 20px; border-bottom: 2px solid #e5e7eb; padding-bottom: 8px;">Curriculum</h3>
        <ul>
            <li><strong>The Profit Centers:</strong> Discover actual digital products you can conceive, build, and list before Sunday night.</li>
            <li><strong>The Attention System:</strong> Learn how to use AI-powered ads to put your product directly in front of buyers.</li>
            <li><strong>The Automation Layer:</strong> Build the system that takes a total stranger from "never heard of you" to "money in your account" completely hands-free.</li>
        </ul>
        
        <h3 style="color: #1a1a1a; font-size: 20px; border-bottom: 2px solid #e5e7eb; padding-bottom: 8px;">Tools Needed</h3>
        <ul>
            <li>A laptop or desktop computer with a stable internet connection.</li>
            <li>Google Chrome browser.</li>
            <li>A free ChatGPT account.</li>
            <li>Your full attention.</li>
        </ul>

        <div style="background-color: #f0fdf4; border: 1px solid #bbf7d0; border-radius: 8px; padding: 18px; margin-top: 15px;">
            <p style="margin: 0 0 8px 0; color: #166534; font-weight: bold; font-size: 15px;">💡 Optional: Build Along With Me via Abacus AI ($10)</p>
            <p style="margin: 0 0 10px 0; color: #374151; font-size: 14px; line-height: 1.5;">
                If you want to build along with me live on screen as I build, you can optionally sign up for 
                <a href="https://chatllm.abacus.ai/GfBKHBRnfN" style="color: #0f6b4d; font-weight: bold; text-decoration: underline;">Abacus AI using this link</a>.
            </p>
            <p style="margin: 0; color: #4b5563; font-size: 13px; line-height: 1.5;">
                This will give you access to top-tier AI models like <strong>Claude</strong>, <strong>ChatGPT</strong>, <strong>Nano Banana</strong>, and <strong>Kimi</strong> for a fraction of the original cost of each individual model ($10).
            </p>
        </div>
    """
    html_body = get_base_html("Meeting Link", content, app_name="AI Weekend", footer_text="&copy; 2026 Career Dev Network. All rights reserved.")
    return send_zeptomail(email, subject, html_body)

def send_abandoned_cart_email(email, name, level=1):
    greeting_name = name.split()[0].title() if name and name.strip() else "there"

    if level == 1:
        subject = "Did you forget something? (Your AI-Weekend Seat)"
        body_text = "We noticed you started checking out for the <strong>AI-Weekend Masterclass</strong>, but didn't finish. Seats are strictly limited to keep the live build session interactive."
    elif level == 2:
        subject = "Your seat is still reserved (for now)"
        body_text = "Registration is filling up quickly. You started checking out, but your seat hasn't been confirmed yet. Don't let your 11:47pm moment slip away."
    else:
        subject = "Final reminder: Your AI-Weekend spot is about to close"
        body_text = "This is our last reminder. Your temporary hold is expiring and your spot will be released to someone on the waiting list."

    content = f"""
        <div style="background: linear-gradient(135deg, #091a10 0%, #030805 100%); padding: 30px; border-radius: 12px; margin-bottom: 24px; color: #fff; border: 1px solid #1a3a25;">
            <span style="display: inline-block; background-color: rgba(74, 222, 128, 0.15); color: #4ade80; padding: 4px 12px; border-radius: 9999px; font-size: 12px; font-weight: bold; letter-spacing: 1px; text-transform: uppercase; margin-bottom: 12px;">INCOMPLETE REGISTRATION</span>
            <h2 style="color: #ffffff; margin-top: 0; margin-bottom: 12px; font-size: 22px;">Hi {greeting_name},</h2>
            <p style="color: #d1d5db; font-size: 16px; line-height: 1.6; margin: 0;">{body_text}</p>
        </div>
        
        <div style="background-color: #f8fafc; border: 1px solid #e2e8f0; border-radius: 8px; padding: 20px; margin-bottom: 24px;">
            <h3 style="color: #1a1a1a; margin-top: 0; margin-bottom: 12px; font-size: 16px;">What we will build together live:</h3>
            <ul style="color: #4b5563; font-size: 14px; padding-left: 20px; margin: 0; line-height: 1.7;">
                <li><strong>The Profit Centers:</strong> Conceive, build, and list digital products in a single weekend.</li>
                <li><strong>The Attention System:</strong> Put your offer directly in front of buyers using AI-powered ads.</li>
                <li><strong>The Automation Layer:</strong> Fully automated sales that drop into your account while you sleep.</li>
            </ul>
        </div>

        <p style="color: #374151; font-size: 15px; margin-bottom: 10px;">Your ticket is only <strong>₦5,000</strong> — less than a wrap of chicken shawarma and a drink.</p>
        
        <div style="text-align: center; margin: 32px 0 20px;">
            <a href="https://careerdevnetwork.com/ai-weekend#checkout" style="display: inline-block; background: linear-gradient(180deg, #fef08a 0%, #eab308 100%); color: #000; text-decoration: none; padding: 16px 36px; border-radius: 50px; font-weight: 900; font-size: 16px; box-shadow: 0 4px 15px rgba(234, 179, 8, 0.4); text-transform: uppercase; letter-spacing: 0.5px;">Complete Registration for ₦5,000 →</a>
        </div>
        <p style="text-align: center; color: #9ca3af; font-size: 12px; margin: 0;">If you already completed your payment, please disregard this message.</p>
    """
    html_body = get_base_html("Finish your registration", content, app_name="AI Weekend", footer_text="&copy; 2026 Career Dev Network. All rights reserved.")
    return send_zeptomail(email, subject, html_body)
