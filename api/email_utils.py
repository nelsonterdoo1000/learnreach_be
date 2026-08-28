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
