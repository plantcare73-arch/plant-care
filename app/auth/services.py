"""
Authentication domain services.
Includes password reset token generation and email mocking.
"""

import os
from datetime import datetime, timedelta, timezone
from flask import current_app, url_for
from itsdangerous import URLSafeTimedSerializer

def generate_reset_token(email):
    """Generate a secure, time-limited token for password reset."""
    serializer = URLSafeTimedSerializer(current_app.config['SECRET_KEY'])
    return serializer.dumps(email, salt='password-reset-salt')


def verify_reset_token(token, max_age=3600):
    """Verify a reset token. Returns the email if valid, or None."""
    serializer = URLSafeTimedSerializer(current_app.config['SECRET_KEY'])
    try:
        email = serializer.loads(
            token,
            salt='password-reset-salt',
            max_age=max_age
        )
        return email
    except Exception:
        return None


def send_password_reset_email(user_email, user_name, token):
    """
    Mock sending a password reset email.
    In a real system, this would use SMTP or SendGrid/AWS SES.
    """
    reset_url = url_for('auth.reset_password', token=token, _external=True)
    
    # We mock it by logging it
    current_app.logger.info("=" * 60)
    current_app.logger.info("MOCK EMAIL SENT TO: %s", user_email)
    current_app.logger.info("SUBJECT: Reset Your AI Plant Care Password")
    current_app.logger.info("BODY:")
    current_app.logger.info(f"Hi {user_name},")
    current_app.logger.info("You requested a password reset.")
    current_app.logger.info("Please click the link below to reset it:")
    current_app.logger.info(reset_url)
    current_app.logger.info("This link expires in 1 hour.")
    current_app.logger.info("=" * 60)
