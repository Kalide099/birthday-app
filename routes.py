"""
Flask routes and blueprints
"""
from flask import Blueprint, render_template, request, jsonify, redirect, url_for, flash
from flask_login import login_required, current_user, login_user, logout_user
from app_factory import db, limiter, csrf
from models import User, Friend, BirthdayMessage, Alert
from services import generate_birthday_message
from datetime import datetime, timedelta
import logging

logger = logging.getLogger(__name__)

# Blueprints
main_bp = Blueprint('main', __name__)
auth_bp = Blueprint('auth', __name__)
api_bp = Blueprint('api', __name__)

# Exempt API endpoints from CSRF (they'll use other authentication)
# Also exempt auth for now to simplify development
csrf.exempt(api_bp)
csrf.exempt(auth_bp)


# ============= Main Routes =============

@main_bp.route('/')
@login_required
def index():
    """Main dashboard"""
    return render_template('index.html')


# ============= Authentication Routes =============

@auth_bp.route('/login', methods=['GET', 'POST'])
@limiter.limit("10 per minute")
def login():
    """User login"""
    if current_user.is_authenticated:
        return redirect(url_for('main.index'))
    
    if request.method == 'POST':
        data = request.json if request.is_json else request.form
        username = data.get('username')
        password = data.get('password')
        
        user = User.query.filter_by(username=username).first()
        
        logger.info(f"Login attempt - Username: '{username}', Password length: {len(password) if password else 0}, User found: {user is not None}")
        
        if user and user.check_password(password):
            login_user(user, remember=True)
            logger.info(f"User {username} logged in successfully")
            
            if request.is_json:
                return jsonify({'success': True, 'redirect': url_for('main.index')})
            return redirect(url_for('main.index'))
        
        error_msg = 'Invalid username or password'
        logger.warning(f"Failed login attempt for username: '{username}' - Password check: {user.check_password(password) if user else 'No user found'}")
        
        if request.is_json:
            return jsonify({'success': False, 'error': error_msg}), 401
        flash(error_msg, 'error')
    
    return render_template('login.html')


@auth_bp.route('/register', methods=['GET', 'POST'])
@limiter.limit("5 per hour")
def register():
    """User registration"""
    if current_user.is_authenticated:
        return redirect(url_for('main.index'))
    
    if request.method == 'POST':
        data = request.json if request.is_json else request.form
        username = data.get('username')
        email = data.get('email')
        password = data.get('password')
        
        # Validate input
        if not username or not email or not password:
            error_msg = 'All fields are required'
            if request.is_json:
                return jsonify({'success': False, 'error': error_msg}), 400
            flash(error_msg, 'error')
            return render_template('register.html')
        
        # Check if user exists
        if User.query.filter_by(username=username).first():
            error_msg = 'Username already exists'
            if request.is_json:
                return jsonify({'success': False, 'error': error_msg}), 400
            flash(error_msg, 'error')
            return render_template('register.html')
        
        if User.query.filter_by(email=email).first():
            error_msg = 'Email already registered'
            if request.is_json:
                return jsonify({'success': False, 'error': error_msg}), 400
            flash(error_msg, 'error')
            return render_template('register.html')
        
        # Create new user
        user = User(username=username, email=email)
        user.set_password(password)
        db.session.add(user)
        db.session.commit()
        
        logger.info(f"New user registered: {username}")
        
        if request.is_json:
            return jsonify({'success': True, 'redirect': url_for('auth.login')}), 201
        flash('Registration successful! Please log in.', 'success')
        return redirect(url_for('auth.login'))
    
    return render_template('register.html')


@auth_bp.route('/logout')
@login_required
def logout():
    """User logout"""
    logger.info(f"User {current_user.username} logged out")
    logout_user()
    return redirect(url_for('auth.login'))


@auth_bp.route('/forgot-password', methods=['GET', 'POST'])
@limiter.limit("3 per hour")
def forgot_password():
    """Forgot password - send reset email"""
    if current_user.is_authenticated:
        return redirect(url_for('main.index'))
    
    if request.method == 'POST':
        email = request.form.get('email')
        user = User.query.filter_by(email=email).first()
        
        if user:
            token = user.get_reset_token()
            from services import send_password_reset_email
            if send_password_reset_email(user, token):
                flash('A password reset link has been sent to your email.', 'success')
                logger.info(f"Password reset email sent to {email}")
            else:
                flash('Error sending email. Please try again later.', 'error')
                logger.error(f"Failed to send password reset email to {email}")
        else:
            # Don't reveal if email exists or not for security
            flash('If that email is registered, a password reset link will be sent.', 'info')
            logger.warning(f"Password reset attempted for non-existent email: {email}")
        
        return redirect(url_for('auth.login'))
    
    return render_template('forgot_password.html')


@auth_bp.route('/reset-password/<token>', methods=['GET', 'POST'])
@limiter.limit("5 per hour")
def reset_password(token):
    """Reset password with token"""
    if current_user.is_authenticated:
        return redirect(url_for('main.index'))
    
    user = User.verify_reset_token(token)
    if not user:
        flash('Invalid or expired reset link.', 'error')
        return redirect(url_for('auth.forgot_password'))
    
    if request.method == 'POST':
        password = request.form.get('password')
        confirm_password = request.form.get('confirm_password')
        
        if not password or len(password) < 6:
            flash('Password must be at least 6 characters long.', 'error')
            return render_template('reset_password.html')
        
        if password != confirm_password:
            flash('Passwords do not match.', 'error')
            return render_template('reset_password.html')
        
        user.set_password(password)
        db.session.commit()
        flash('Your password has been reset! You can now log in.', 'success')
        logger.info(f"Password reset successful for user {user.username}")
        return redirect(url_for('auth.login'))
    
    return render_template('reset_password.html')


# ============= API Routes =============

@api_bp.route('/friends', methods=['GET'])
@login_required
@limiter.limit("100 per hour")
def get_friends():
    """Get all friends for current user"""
    friends = current_user.friends.order_by(Friend.name).all()
    return jsonify([{
        'id': f.id,
        'name': f.name,
        'birthday': f.birthday.strftime('%Y-%m-%d'),
        'email': f.email,
        'phone': f.phone,
        'relationship': f.relationship,
        'notes': f.notes
    } for f in friends])


@api_bp.route('/friends', methods=['POST'])
@login_required
@limiter.limit("50 per hour")
def add_friend():
    """Add a new friend"""
    data = request.json
    try:
        birthday = datetime.strptime(data['birthday'], '%Y-%m-%d').date()
        friend = Friend(
            user_id=current_user.id,
            name=data['name'],
            birthday=birthday,
            email=data.get('email', ''),
            phone=data.get('phone', ''),
            relationship=data.get('relationship', ''),
            notes=data.get('notes', '')
        )
        db.session.add(friend)
        db.session.commit()
        logger.info(f"Friend {friend.name} added by user {current_user.username}")
        return jsonify({'success': True, 'id': friend.id}), 201
    except Exception as e:
        logger.error(f"Error adding friend: {e}")
        return jsonify({'success': False, 'error': str(e)}), 400


@api_bp.route('/friends/<int:friend_id>', methods=['PUT'])
@login_required
@limiter.limit("50 per hour")
def update_friend(friend_id):
    """Update a friend"""
    friend = Friend.query.filter_by(id=friend_id, user_id=current_user.id).first_or_404()
    data = request.json
    try:
        friend.name = data.get('name', friend.name)
        if 'birthday' in data:
            friend.birthday = datetime.strptime(data['birthday'], '%Y-%m-%d').date()
        friend.email = data.get('email', friend.email)
        friend.phone = data.get('phone', friend.phone)
        friend.relationship = data.get('relationship', friend.relationship)
        friend.notes = data.get('notes', friend.notes)
        db.session.commit()
        logger.info(f"Friend {friend.name} updated by user {current_user.username}")
        return jsonify({'success': True})
    except Exception as e:
        logger.error(f"Error updating friend: {e}")
        return jsonify({'success': False, 'error': str(e)}), 400


@api_bp.route('/friends/<int:friend_id>', methods=['DELETE'])
@login_required
@limiter.limit("50 per hour")
def delete_friend(friend_id):
    """Delete a friend"""
    friend = Friend.query.filter_by(id=friend_id, user_id=current_user.id).first_or_404()
    db.session.delete(friend)
    db.session.commit()
    logger.info(f"Friend {friend.name} deleted by user {current_user.username}")
    return jsonify({'success': True})


@api_bp.route('/alerts', methods=['GET'])
@login_required
@limiter.limit("100 per hour")
def get_alerts():
    """Get alerts for current user's friends"""
    friend_ids = [f.id for f in current_user.friends]
    alerts = Alert.query.filter(Alert.friend_id.in_(friend_ids)).order_by(Alert.created_at.desc()).limit(50).all()
    return jsonify([{
        'id': a.id,
        'friend_id': a.friend_id,
        'alert_type': a.alert_type,
        'message': a.message,
        'created_at': a.created_at.strftime('%Y-%m-%d %H:%M:%S'),
        'is_read': a.is_read
    } for a in alerts])


@api_bp.route('/alerts/<int:alert_id>/read', methods=['PUT'])
@login_required
def mark_alert_read(alert_id):
    """Mark alert as read"""
    alert = Alert.query.get_or_404(alert_id)
    # Verify user owns this alert's friend
    if alert.friend.user_id != current_user.id:
        return jsonify({'error': 'Unauthorized'}), 403
    alert.is_read = True
    db.session.commit()
    return jsonify({'success': True})


@api_bp.route('/messages/<int:friend_id>', methods=['GET'])
@login_required
def get_friend_messages(friend_id):
    """Get messages for a friend"""
    friend = Friend.query.filter_by(id=friend_id, user_id=current_user.id).first_or_404()
    messages = BirthdayMessage.query.filter_by(friend_id=friend_id).order_by(BirthdayMessage.sent_at.desc()).all()
    return jsonify([{
        'id': m.id,
        'message': m.message,
        'sent_at': m.sent_at.strftime('%Y-%m-%d %H:%M:%S'),
        'year': m.year,
        'email_sent': m.email_sent
    } for m in messages])


@api_bp.route('/upcoming-birthdays', methods=['GET'])
@login_required
@limiter.limit("100 per hour")
def get_upcoming_birthdays():
    """Get upcoming birthdays for current user"""
    today = datetime.now().date()
    friends = current_user.friends.all()
    
    upcoming = []
    for friend in friends:
        birthday_this_year = friend.birthday.replace(year=today.year)
        if birthday_this_year < today:
            birthday_this_year = friend.birthday.replace(year=today.year + 1)
        
        days_until = (birthday_this_year - today).days
        
        if days_until <= 30:
            upcoming.append({
                'id': friend.id,
                'name': friend.name,
                'birthday': birthday_this_year.strftime('%Y-%m-%d'),
                'days_until': days_until
            })
    
    upcoming.sort(key=lambda x: x['days_until'])
    return jsonify(upcoming)
