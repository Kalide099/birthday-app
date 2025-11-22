"""
Database models for Birthday Reminder App
"""
from app_factory import db, login_manager
from flask_login import UserMixin
from werkzeug.security import generate_password_hash, check_password_hash
from datetime import datetime
from itsdangerous import URLSafeTimedSerializer
from flask import current_app


@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))


class User(UserMixin, db.Model):
    """User model for authentication"""
    __tablename__ = 'users'
    
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), unique=True, nullable=False, index=True)
    email = db.Column(db.String(120), unique=True, nullable=False, index=True)
    password_hash = db.Column(db.String(255), nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    is_active = db.Column(db.Boolean, default=True)
    
    # Relationships
    friends = db.relationship('Friend', backref='user', lazy='dynamic', cascade='all, delete-orphan')
    
    def set_password(self, password):
        """Hash and set password"""
        self.password_hash = generate_password_hash(password)
    
    def check_password(self, password):
        """Check if password matches"""
        return check_password_hash(self.password_hash, password)
    
    def get_reset_token(self, expires_sec=1800):
        """Generate a password reset token (valid for 30 minutes)"""
        s = URLSafeTimedSerializer(current_app.config['SECRET_KEY'])
        return s.dumps({'user_id': self.id}, salt='password-reset-salt')
    
    @staticmethod
    def verify_reset_token(token, expires_sec=1800):
        """Verify password reset token"""
        s = URLSafeTimedSerializer(current_app.config['SECRET_KEY'])
        try:
            user_id = s.loads(token, salt='password-reset-salt', max_age=expires_sec)['user_id']
        except:
            return None
        return User.query.get(user_id)
    
    def __repr__(self):
        return f'<User {self.username}>'


class Friend(db.Model):
    """Friend model for storing birthday information"""
    __tablename__ = 'friends'
    
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False, index=True)
    name = db.Column(db.String(100), nullable=False)
    birthday = db.Column(db.Date, nullable=False, index=True)
    email = db.Column(db.String(120))
    phone = db.Column(db.String(20))
    relationship = db.Column(db.String(50))
    notes = db.Column(db.Text)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationships
    messages = db.relationship('BirthdayMessage', backref='friend', lazy='dynamic', cascade='all, delete-orphan')
    alerts = db.relationship('Alert', backref='friend', lazy='dynamic', cascade='all, delete-orphan')
    
    def __repr__(self):
        return f'<Friend {self.name}>'


class BirthdayMessage(db.Model):
    """Birthday message model"""
    __tablename__ = 'birthday_messages'
    
    id = db.Column(db.Integer, primary_key=True)
    friend_id = db.Column(db.Integer, db.ForeignKey('friends.id'), nullable=False, index=True)
    message = db.Column(db.Text, nullable=False)
    sent_at = db.Column(db.DateTime, default=datetime.utcnow)
    year = db.Column(db.Integer, nullable=False, index=True)
    email_sent = db.Column(db.Boolean, default=False)
    
    def __repr__(self):
        return f'<BirthdayMessage for Friend {self.friend_id}>'


class Alert(db.Model):
    """Alert model for notifications"""
    __tablename__ = 'alerts'
    
    id = db.Column(db.Integer, primary_key=True)
    friend_id = db.Column(db.Integer, db.ForeignKey('friends.id'), nullable=False, index=True)
    alert_type = db.Column(db.String(20), nullable=False, index=True)  # 'reminder' or 'birthday'
    message = db.Column(db.Text, nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow, index=True)
    is_read = db.Column(db.Boolean, default=False, index=True)
    
    def __repr__(self):
        return f'<Alert {self.alert_type} for Friend {self.friend_id}>'
