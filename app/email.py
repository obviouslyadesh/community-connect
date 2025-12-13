import os
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from flask import current_app

def send_email(to_email, subject, html_content, text_content=None):
    smtp_server = os.environ.get('SMTP_SERVER', 'smtp.gmail.com')
    smtp_port = int(os.environ.get('SMTP_PORT', 587))
    smtp_username = os.environ.get('SMTP_USERNAME')
    smtp_password = os.environ.get('SMTP_PASSWORD')
    from_email = os.environ.get('FROM_EMAIL', smtp_username)
    
    if not all([smtp_username, smtp_password]):
        return False
    
    try:
        msg = MIMEMultipart('alternative')
        msg['Subject'] = subject
        msg['From'] = from_email
        msg['To'] = to_email
        
        if text_content:
            part1 = MIMEText(text_content, 'plain')
            msg.attach(part1)
        
        part2 = MIMEText(html_content, 'html')
        msg.attach(part2)
        
        with smtplib.SMTP(smtp_server, smtp_port) as server:
            server.starttls()
            server.login(smtp_username, smtp_password)
            server.send_message(msg)
        
        return True
        
    except Exception:
        return False

def send_password_reset_email(user, token):
    reset_url = f"{current_app.config.get('BASE_URL', 'http://localhost:5001')}/reset-password/{token}"
    
    subject = "Reset Your Password - Community Connect"
    
    html_content = f"""
    <!DOCTYPE html>
    <html>
    <head>
        <style>
            body {{ font-family: Arial, sans-serif; line-height: 1.6; color: #333; }}
            .container {{ max-width: 600px; margin: 0 auto; padding: 20px; }}
            .header {{ background: #4285f4; color: white; padding: 20px; text-align: center; }}
            .content {{ padding: 30px; background: #f9f9f9; }}
            .button {{ display: inline-block; padding: 12px 24px; background: #4285f4; color: white; 
                     text-decoration: none; border-radius: 5px; margin: 20px 0; }}
            .footer {{ text-align: center; padding: 20px; color: #666; font-size: 12px; }}
        </style>
    </head>
    <body>
        <div class="container">
            <div class="header">
                <h1>Community Connect</h1>
            </div>
            <div class="content">
                <h2>Reset Your Password</h2>
                <p>Hello {user.username},</p>
                <p>We received a request to reset your password. Click the button below to create a new password:</p>
                
                <p style="text-align: center;">
                    <a href="{reset_url}" class="button">Reset Password</a>
                </p>
                
                <p>Or copy and paste this link in your browser:</p>
                <p style="background: #eee; padding: 10px; border-radius: 5px; word-break: break-all;">
                    {reset_url}
                </p>
                
                <p>This link will expire in 1 hour for security reasons.</p>
                <p>If you didn't request a password reset, you can safely ignore this email.</p>
            </div>
            <div class="footer">
                <p>© 2024 Community Connect. All rights reserved.</p>
                <p>This is an automated message, please do not reply to this email.</p>
            </div>
        </div>
    </body>
    </html>
    """
    
    text_content = f"""
    Reset Your Password - Community Connect
    
    Hello {user.username},
    
    We received a request to reset your password. Use the link below to create a new password:
    
    {reset_url}
    
    This link will expire in 1 hour for security reasons.
    
    If you didn't request a password reset, you can safely ignore this email.
    
    © 2024 Community Connect
    """
    
    return send_email(user.email, subject, html_content, text_content)