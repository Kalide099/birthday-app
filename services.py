"""
Service layer for business logic
"""
from datetime import datetime, timedelta
import openai
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
import os
from app_factory import db
from models import Friend, BirthdayMessage, Alert
import logging

logger = logging.getLogger(__name__)


def send_email(to_email, subject, message):
    """Send email to friend"""
    try:
        smtp_server = os.getenv('SMTP_SERVER', 'smtp.gmail.com')
        smtp_port = int(os.getenv('SMTP_PORT', 587))
        smtp_email = os.getenv('SMTP_EMAIL')
        smtp_password = os.getenv('SMTP_PASSWORD')
        
        if not smtp_email or not smtp_password:
            logger.warning("Email credentials not configured")
            return False
        
        if not to_email:
            logger.warning("No email address provided")
            return False
        
        # Create message
        msg = MIMEMultipart('alternative')
        msg['From'] = smtp_email
        msg['To'] = to_email
        msg['Subject'] = subject
        
        # Create HTML version
        html = f"""
        <html>
            <body style="font-family: Arial, sans-serif; padding: 20px; background-color: #f5f5f5;">
                <div style="max-width: 600px; margin: 0 auto; background-color: white; padding: 30px; border-radius: 10px; box-shadow: 0 2px 10px rgba(0,0,0,0.1);">
                    <h1 style="color: #667eea; text-align: center;">🎉 Happy Birthday! 🎂</h1>
                    <p style="font-size: 16px; line-height: 1.6; color: #333;">
                        {message}
                    </p>
                    <p style="font-size: 14px; color: #666; margin-top: 30px;">
                        Best wishes,<br>
                        Your Friend
                    </p>
                </div>
            </body>
        </html>
        """
        
        msg.attach(MIMEText(html, 'html'))
        
        # Send email
        with smtplib.SMTP(smtp_server, smtp_port) as server:
            server.starttls()
            server.login(smtp_email, smtp_password)
            server.send_message(msg)
        
        logger.info(f"Email sent successfully to {to_email}")
        return True
    except Exception as e:
        logger.error(f"Error sending email to {to_email}: {e}")
        return False


def send_password_reset_email(user, token):
    """Send password reset email to user"""
    try:
        smtp_server = os.getenv('SMTP_SERVER', 'smtp.gmail.com')
        smtp_port = int(os.getenv('SMTP_PORT', 587))
        smtp_email = os.getenv('SMTP_EMAIL')
        smtp_password = os.getenv('SMTP_PASSWORD')
        
        logger.info(f"Attempting to send password reset email to {user.email}")
        logger.info(f"SMTP Config - Server: {smtp_server}, Port: {smtp_port}, Email: {smtp_email}, Password set: {bool(smtp_password)}")
        
        if not smtp_email or not smtp_password:
            logger.error("Email credentials not configured - SMTP_EMAIL or SMTP_PASSWORD missing")
            return False
        
        # Create reset URL using environment variable or default to localhost
        base_url = os.getenv('APP_URL', 'http://127.0.0.1:5000')
        reset_url = f"{base_url}/auth/reset-password/{token}"
        
        # Create message
        msg = MIMEMultipart('alternative')
        msg['From'] = smtp_email
        msg['To'] = user.email
        msg['Subject'] = 'Password Reset Request - Birthday Reminder App'
        
        # Create HTML version
        html = f"""
        <html>
            <body style="font-family: Arial, sans-serif; padding: 20px; background-color: #f5f5f5;">
                <div style="max-width: 600px; margin: 0 auto; background-color: white; padding: 30px; border-radius: 10px; box-shadow: 0 2px 10px rgba(0,0,0,0.1);">
                    <h1 style="color: #667eea; text-align: center;">🔒 Password Reset Request</h1>
                    <p style="font-size: 16px; line-height: 1.6; color: #333;">
                        Hi {user.username},
                    </p>
                    <p style="font-size: 16px; line-height: 1.6; color: #333;">
                        We received a request to reset your password for the Birthday Reminder App. 
                        Click the button below to reset your password:
                    </p>
                    <div style="text-align: center; margin: 30px 0;">
                        <a href="{reset_url}" style="background-color: #667eea; color: white; padding: 15px 30px; text-decoration: none; border-radius: 8px; display: inline-block; font-weight: bold;">
                            Reset Password
                        </a>
                    </div>
                    <p style="font-size: 14px; line-height: 1.6; color: #666;">
                        Or copy and paste this link into your browser:<br>
                        <a href="{reset_url}" style="color: #667eea;">{reset_url}</a>
                    </p>
                    <p style="font-size: 14px; line-height: 1.6; color: #666;">
                        This link will expire in 30 minutes.
                    </p>
                    <p style="font-size: 14px; color: #999; margin-top: 30px; border-top: 1px solid #eee; padding-top: 20px;">
                        If you didn't request a password reset, please ignore this email or contact support if you have concerns.
                    </p>
                </div>
            </body>
        </html>
        """
        
        msg.attach(MIMEText(html, 'html'))
        
        # Send email
        logger.info(f"Connecting to SMTP server: {smtp_server}:{smtp_port}")
        with smtplib.SMTP(smtp_server, smtp_port, timeout=30) as server:
            logger.info("Starting TLS...")
            server.starttls()
            logger.info("Logging in to SMTP server...")
            server.login(smtp_email, smtp_password)
            logger.info("Sending message...")
            server.send_message(msg)
        
        logger.info(f"✅ Password reset email sent successfully to {user.email}")
        return True
    except smtplib.SMTPAuthenticationError as e:
        logger.error(f"❌ SMTP Authentication failed: {e}. Check your Gmail App Password!")
        return False
    except smtplib.SMTPException as e:
        logger.error(f"❌ SMTP Error sending password reset email: {e}")
        return False
    except Exception as e:
        logger.error(f"❌ Unexpected error sending password reset email to {user.email}: {type(e).__name__}: {e}")
        import traceback
        logger.error(traceback.format_exc())
        return False


def generate_birthday_message(friend_name, relationship=None):
    """Generate a personalized birthday message using AI"""
    try:
        prompt = f"Write a warm, heartfelt birthday message for {friend_name}"
        if relationship:
            prompt += f", who is my {relationship}"
        prompt += ". Make it personal, genuine, and cheerful. Keep it to 2-3 sentences."
        
        response = openai.chat.completions.create(
            model="gpt-3.5-turbo",
            messages=[
                {"role": "system", "content": "You are a friendly assistant that writes heartfelt birthday messages."},
                {"role": "user", "content": prompt}
            ],
            max_tokens=150,
            temperature=0.8
        )
        
        message = response.choices[0].message.content.strip()
        logger.info(f"AI message generated for {friend_name}")
        return message
    except Exception as e:
        logger.warning(f"Error generating AI message: {e}")
        return f"Happy Birthday {friend_name}! 🎉 Wishing you an amazing day filled with love, joy, and wonderful memories!"


def check_birthdays(app):
    """Check for upcoming and today's birthdays"""
    with app.app_context():
        today = datetime.now().date()
        tomorrow = today + timedelta(days=1)
        
        friends = Friend.query.all()
        
        for friend in friends:
            try:
                birthday_this_year = friend.birthday.replace(year=today.year)
                
                # Check if birthday is tomorrow (reminder alert)
                if birthday_this_year == tomorrow:
                    existing_alert = Alert.query.filter_by(
                        friend_id=friend.id,
                        alert_type='reminder'
                    ).filter(
                        db.func.date(Alert.created_at) == today
                    ).first()
                    
                    if not existing_alert:
                        alert = Alert(
                            friend_id=friend.id,
                            alert_type='reminder',
                            message=f"⏰ Reminder: {friend.name}'s birthday is tomorrow!"
                        )
                        db.session.add(alert)
                        logger.info(f"Reminder alert created for {friend.name}")
                
                # Check if birthday is today
                if birthday_this_year == today:
                    existing_message = BirthdayMessage.query.filter_by(
                        friend_id=friend.id,
                        year=today.year
                    ).first()
                    
                    if not existing_message:
                        # Generate AI birthday message
                        ai_message = generate_birthday_message(friend.name, friend.relationship)
                        
                        # Send email if available
                        email_sent = False
                        if friend.email:
                            email_sent = send_email(
                                friend.email,
                                f"🎉 Happy Birthday {friend.name}!",
                                ai_message
                            )
                        
                        # Save the message
                        message = BirthdayMessage(
                            friend_id=friend.id,
                            message=ai_message,
                            year=today.year,
                            email_sent=email_sent
                        )
                        db.session.add(message)
                        
                        # Create birthday alert
                        email_status = "✉️ Email sent!" if email_sent else ("📧 No email address" if not friend.email else "❌ Email failed")
                        alert = Alert(
                            friend_id=friend.id,
                            alert_type='birthday',
                            message=f"🎂 {friend.name}'s birthday is today! {email_status} Message: {ai_message}"
                        )
                        db.session.add(alert)
                        logger.info(f"Birthday message created for {friend.name}")
                
                db.session.commit()
            except Exception as e:
                logger.error(f"Error processing birthday for {friend.name}: {e}")
                db.session.rollback()
