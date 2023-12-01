from flask_mail import Message
from app import mail
import os

def send_verification_email(email, token):
    verification_link = f"{os.getenv('FE_URL')}/verify-email/{token}"
    msg = Message("Email Verification", sender=os.getenv('MAIL_USERNAME'), recipients=[email])
    msg.body = f"Click on the link to verify your email: {verification_link}"
    mail.send(msg)
    
def send_password_reset_email(email, reset_token):
    reset_link = f"{os.getenv('FE_URL')}/reset-password/{reset_token}"
    msg = Message("Password Reset", sender=os.getenv('MAIL_USERNAME'), recipients=[email])
    msg.body = f"To reset your password, click the following link: {reset_link}"
    mail.send(msg)