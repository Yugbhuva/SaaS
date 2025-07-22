import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from config import Config

def send_email(to_email, subject, body, html_body=None):
    """Send email using SMTP configuration"""
    try:
        msg = MIMEMultipart('alternative')
        msg['Subject'] = subject
        msg['From'] = Config.MAIL_USERNAME
        msg['To'] = to_email
        
        # Add text part
        text_part = MIMEText(body, 'plain')
        msg.attach(text_part)
        
        # Add HTML part if provided
        if html_body:
            html_part = MIMEText(html_body, 'html')
            msg.attach(html_part)
        
        # Send email
        server = smtplib.SMTP(Config.MAIL_SERVER, Config.MAIL_PORT)
        if Config.MAIL_USE_TLS:
            server.starttls()
        server.login(Config.MAIL_USERNAME, Config.MAIL_PASSWORD)
        server.send_message(msg)
        server.quit()
        
        return True
    except Exception as e:
        print(f"Email sending failed: {e}")
        return False

def send_welcome_email(user_email, user_name):
    """Send welcome email to new users"""
    subject = f"Welcome to {Config.APP_NAME}!"
    body = f"""
    Hi {user_name},
    
    Welcome to {Config.APP_NAME}! Your account has been created successfully.
    
    You can now log in and start using our services.
    
    Best regards,
    The {Config.APP_NAME} Team
    """
    
    return send_email(user_email, subject, body)

def send_subscription_confirmation(user_email, plan_name):
    """Send subscription confirmation email"""
    subject = "Subscription Confirmed!"
    body = f"""
    Your subscription to {plan_name} has been confirmed.
    
    You now have access to all premium features.
    
    Thank you for your business!
    """
    
    return send_email(user_email, subject, body)