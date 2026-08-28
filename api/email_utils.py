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

def get_base_html(title, content):
    return f"""
    <!DOCTYPE html>
    <html>
    <head>
        <meta charset="utf-8">
        <meta name="viewport" content="width=device-width, initial-scale=1.0">
    </head>
    <body style="font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif; background-color: #f4f7f6; margin: 0; padding: 40px 20px;">
        <div style="max-width: 600px; margin: 0 auto; background-color: #ffffff; border-radius: 12px; overflow: hidden; box-shadow: 0 4px 15px rgba(0,0,0,0.05);">
            <div style="background-color: #2e7d32; padding: 30px; text-align: center;">
                <h1 style="color: #ffffff; margin: 0; font-size: 28px; font-weight: 600; letter-spacing: 1px;">LearnReach</h1>
            </div>
            <div style="padding: 40px 30px;">
                <h2 style="color: #1a1a1a; margin-top: 0; margin-bottom: 24px; font-size: 22px;">{title}</h2>
                <div style="color: #4a5568; font-size: 16px; line-height: 1.6;">
                    {content}
                </div>
            </div>
            <div style="background-color: #f8fafc; padding: 20px; text-align: center; border-top: 1px solid #edf2f7;">
                <p style="margin: 0; color: #718096; font-size: 14px;">&copy; 2026 LearnReach. All rights reserved.</p>
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
