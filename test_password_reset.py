"""
Test password reset email functionality
"""
from wsgi import app
from models import User
from services import send_password_reset_email

def test_password_reset_email():
    """Test sending password reset email"""
    with app.app_context():
        # Get admin user
        admin = User.query.filter_by(username='admin').first()
        
        if not admin:
            print("❌ Admin user not found. Run reset_admin.py first!")
            return
        
        print(f"📧 Testing password reset email for: {admin.email}")
        print(f"   Username: {admin.username}")
        print()
        
        # Generate token
        token = admin.get_reset_token()
        print(f"🔑 Token generated: {token[:50]}...")
        print()
        
        # Try sending email
        print("📤 Sending password reset email...")
        success = send_password_reset_email(admin, token)
        
        if success:
            print("✅ Password reset email sent successfully!")
            print(f"   Check inbox: {admin.email}")
        else:
            print("❌ Failed to send password reset email!")
            print("   Check the logs above for details.")

if __name__ == '__main__':
    test_password_reset_email()
