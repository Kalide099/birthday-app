from flask import Flask, render_template, request, jsonify
from flask_sqlalchemy import SQLAlchemy
from datetime import datetime, timedelta
import os
from apscheduler.schedulers.background import BackgroundScheduler
import openai
from dotenv import load_dotenv
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart

load_dotenv()

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///birthdays.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['SECRET_KEY'] = os.getenv('SECRET_KEY', 'your-secret-key-here')

db = SQLAlchemy(app)

# OpenAI API Configuration
openai.api_key = os.getenv('OPENAI_API_KEY')

# Models
class Friend(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    birthday = db.Column(db.Date, nullable=False)
    email = db.Column(db.String(120))
    phone = db.Column(db.String(20))
    relationship = db.Column(db.String(50))
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

class BirthdayMessage(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    friend_id = db.Column(db.Integer, db.ForeignKey('friend.id'), nullable=False)
    message = db.Column(db.Text, nullable=False)
    sent_at = db.Column(db.DateTime, default=datetime.utcnow)
    year = db.Column(db.Integer, nullable=False)

class Alert(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    friend_id = db.Column(db.Integer, db.ForeignKey('friend.id'), nullable=False)
    alert_type = db.Column(db.String(20), nullable=False)  # 'reminder' or 'birthday'
    message = db.Column(db.Text, nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    is_read = db.Column(db.Boolean, default=False)

# Email Sender Function
def send_email(to_email, subject, message):
    """Send email to friend"""
    try:
        smtp_server = os.getenv('SMTP_SERVER', 'smtp.gmail.com')
        smtp_port = int(os.getenv('SMTP_PORT', '587'))
        smtp_email = os.getenv('SMTP_EMAIL')
        smtp_password = os.getenv('SMTP_PASSWORD')
        
        if not smtp_email or not smtp_password:
            print("Email credentials not configured in .env file")
            return False
        
        if not to_email:
            print("No email address provided for recipient")
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
        
        # Attach HTML version
        msg.attach(MIMEText(html, 'html'))
        
        # Send email
        with smtplib.SMTP(smtp_server, smtp_port) as server:
            server.starttls()
            server.login(smtp_email, smtp_password)
            server.send_message(msg)
        
        print(f"✅ Email sent successfully to {to_email}")
        return True
    except Exception as e:
        print(f"❌ Error sending email: {e}")
        return False

# AI Message Generator
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
        
        return response.choices[0].message.content.strip()
    except Exception as e:
        print(f"Error generating AI message: {e}")
        return f"Happy Birthday {friend_name}! 🎉 Wishing you an amazing day filled with love, joy, and wonderful memories!"

# Notification and Alert System
def check_birthdays():
    """Check for upcoming and today's birthdays"""
    with app.app_context():
        today = datetime.now().date()
        tomorrow = today + timedelta(days=1)
        
        # Get all friends
        friends = Friend.query.all()
        
        for friend in friends:
            # Create a birthday date for this year
            birthday_this_year = friend.birthday.replace(year=today.year)
            
            # Check if birthday is tomorrow (reminder alert)
            if birthday_this_year == tomorrow:
                # Check if we already sent a reminder this year
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
                    print(f"Reminder alert created for {friend.name}")
            
            # Check if birthday is today (birthday alert and send message)
            if birthday_this_year == today:
                # Check if we already sent a message this year
                existing_message = BirthdayMessage.query.filter_by(
                    friend_id=friend.id,
                    year=today.year
                ).first()
                
                if not existing_message:
                    # Generate AI birthday message
                    ai_message = generate_birthday_message(friend.name, friend.relationship)
                    
                    # Send email if email address is available
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
                        year=today.year
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
                    print(f"Birthday message for {friend.name}: {ai_message} | Email: {email_status}")
        
        db.session.commit()

# API Routes
@app.route('/')
def index():
    return render_template('index.html')

@app.route('/api/friends', methods=['GET'])
def get_friends():
    friends = Friend.query.order_by(Friend.name).all()
    return jsonify([{
        'id': f.id,
        'name': f.name,
        'birthday': f.birthday.strftime('%Y-%m-%d'),
        'email': f.email,
        'phone': f.phone,
        'relationship': f.relationship
    } for f in friends])

@app.route('/api/friends', methods=['POST'])
def add_friend():
    data = request.json
    try:
        birthday = datetime.strptime(data['birthday'], '%Y-%m-%d').date()
        friend = Friend(
            name=data['name'],
            birthday=birthday,
            email=data.get('email', ''),
            phone=data.get('phone', ''),
            relationship=data.get('relationship', '')
        )
        db.session.add(friend)
        db.session.commit()
        return jsonify({'success': True, 'id': friend.id}), 201
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 400

@app.route('/api/friends/<int:friend_id>', methods=['PUT'])
def update_friend(friend_id):
    friend = Friend.query.get_or_404(friend_id)
    data = request.json
    try:
        friend.name = data.get('name', friend.name)
        if 'birthday' in data:
            friend.birthday = datetime.strptime(data['birthday'], '%Y-%m-%d').date()
        friend.email = data.get('email', friend.email)
        friend.phone = data.get('phone', friend.phone)
        friend.relationship = data.get('relationship', friend.relationship)
        db.session.commit()
        return jsonify({'success': True})
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 400

@app.route('/api/friends/<int:friend_id>', methods=['DELETE'])
def delete_friend(friend_id):
    friend = Friend.query.get_or_404(friend_id)
    db.session.delete(friend)
    db.session.commit()
    return jsonify({'success': True})

@app.route('/api/alerts', methods=['GET'])
def get_alerts():
    alerts = Alert.query.order_by(Alert.created_at.desc()).limit(50).all()
    return jsonify([{
        'id': a.id,
        'friend_id': a.friend_id,
        'alert_type': a.alert_type,
        'message': a.message,
        'created_at': a.created_at.strftime('%Y-%m-%d %H:%M:%S'),
        'is_read': a.is_read
    } for a in alerts])

@app.route('/api/alerts/<int:alert_id>/read', methods=['PUT'])
def mark_alert_read(alert_id):
    alert = Alert.query.get_or_404(alert_id)
    alert.is_read = True
    db.session.commit()
    return jsonify({'success': True})

@app.route('/api/messages/<int:friend_id>', methods=['GET'])
def get_friend_messages(friend_id):
    messages = BirthdayMessage.query.filter_by(friend_id=friend_id).order_by(BirthdayMessage.sent_at.desc()).all()
    return jsonify([{
        'id': m.id,
        'message': m.message,
        'sent_at': m.sent_at.strftime('%Y-%m-%d %H:%M:%S'),
        'year': m.year
    } for m in messages])

@app.route('/api/upcoming-birthdays', methods=['GET'])
def get_upcoming_birthdays():
    today = datetime.now().date()
    friends = Friend.query.all()
    
    upcoming = []
    for friend in friends:
        birthday_this_year = friend.birthday.replace(year=today.year)
        if birthday_this_year < today:
            birthday_this_year = friend.birthday.replace(year=today.year + 1)
        
        days_until = (birthday_this_year - today).days
        
        if days_until <= 30:  # Show birthdays within next 30 days
            upcoming.append({
                'id': friend.id,
                'name': friend.name,
                'birthday': birthday_this_year.strftime('%Y-%m-%d'),
                'days_until': days_until
            })
    
    upcoming.sort(key=lambda x: x['days_until'])
    return jsonify(upcoming)

if __name__ == '__main__':
    with app.app_context():
        db.create_all()
    
    # Set up scheduler for checking birthdays
    scheduler = BackgroundScheduler()
    # Check birthdays every hour (you can adjust this)
    scheduler.add_job(func=check_birthdays, trigger="interval", hours=1)
    # Also check at midnight daily
    scheduler.add_job(func=check_birthdays, trigger="cron", hour=0, minute=0)
    scheduler.start()
    
    print("Birthday Reminder App Started!")
    print("Scheduler is running to check birthdays...")
    
    try:
        app.run(debug=True, use_reloader=False)
    except (KeyboardInterrupt, SystemExit):
        scheduler.shutdown()
