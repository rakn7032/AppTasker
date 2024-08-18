from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from email.mime.image import MIMEImage
from email.mime.application import MIMEApplication
import smtplib
import re, os
from datetime import datetime
from django.core.validators import URLValidator
from django.core.exceptions import ValidationError
from urllib.parse import urlparse
from appstore_getpoints.settings import EMAIL_HOST_USER, EMAIL_HOST_PASSWORD

def email_validator(email):
    import re
    # pattern = r'^[\w\.-]+@[\w\.-]+\.\w+$'
    pattern = r'^[\w\.-]+(\+[\w\.-]+)?@[\w\.-]+\.\w+$'
    # re.match(pattern, email)
    if re.match(pattern, email):
        return True
    else:
        return False

def password_validator(password):
    if len(password) < 8:
        return False
    if not any(char.isupper() for char in password):
        return False
    if not re.search(r'[!@#$%^&*()_+{}\[\]:;<>,.?`~]', password):
        return False
    if not any(char.isdigit() for char in password):
        return False
    return True
    
def url_validator(url):
    try:
        validator = URLValidator()
        validator(url)
        parsed_url = urlparse(url)
        return bool(parsed_url.scheme) and bool(parsed_url.netloc)
    except ValidationError:
        return False

def send_otp_email(to_email, subject, otp, user_name):
    try:
        if not (to_email and subject and otp and user_name):
            return False
        
        additional_text = f"""Hi {user_name},

We received a request to reset your AppStore. Please use the OTP below to proceed:

OTP: {otp}

This OTP expires in 5 minutes. If you didn't request this, please ignore this email.

Best,
The AppStore Team"""
        
        email_content = additional_text

        # Create MIMEText object for plain text content
        msgText = MIMEText(email_content, 'plain')
        mail = MIMEMultipart()
        mail.attach(msgText)

        # Set email subject, sender, and recipient
        mail['Subject'] = subject
        mail['From'] = EMAIL_HOST_USER
        mail['To'] = to_email

        # Connect to the SMTP server and send the email
        domain_info = ('smtp.gmail.com', 465)
        s = smtplib.SMTP_SSL(*domain_info)
        s.login(EMAIL_HOST_USER, EMAIL_HOST_PASSWORD)
        s.sendmail(EMAIL_HOST_USER, to_email, mail.as_string())
        s.quit()

        return True
    except Exception as e:
        print(e)
        return False


def send_welcome_email(to_email, subject, user_name):
    try:
        if not (to_email and subject and user_name):
            return False

        additional_text = f"""Dear {user_name},

Welcome to AppStore!

Thank you for signing up! We're excited to have you with us. 
Start exploring apps, earn points, and track your progress right from your profile. Don't forget to upload screenshots of your downloaded apps to claim your points.

Enjoy your journey with AppStore!

Best regards,
The AppStore Team
"""
        
        email_content = additional_text

        # Create MIMEText object for plain text content
        msgText = MIMEText(email_content, 'plain')
        mail = MIMEMultipart()
        mail.attach(msgText)

        # Set email subject, sender, and recipient
        mail['Subject'] = subject
        mail['From'] = EMAIL_HOST_USER
        mail['To'] = to_email

        # Connect to the SMTP server and send the email
        domain_info = ('smtp.gmail.com', 465)
        s = smtplib.SMTP_SSL(*domain_info)
        s.login(EMAIL_HOST_USER, EMAIL_HOST_PASSWORD)
        s.sendmail(EMAIL_HOST_USER, to_email, mail.as_string())
        s.quit()

        return True
    except Exception as e:
        print(f"An error occurred: {e}")
        return False