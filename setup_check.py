"""
Quick setup and test script
"""
import os
import sys

def setup_and_test():
    print("🔍 Birthday Reminder App - Setup Verification\n")
    print("="*60)
    
    # Check Python version
    print("\n1. Checking Python version...")
    if sys.version_info < (3, 8):
        print("   ❌ Python 3.8+ required")
        return False
    print(f"   ✅ Python {sys.version_info.major}.{sys.version_info.minor}")
    
    # Check .env file
    print("\n2. Checking .env file...")
    if not os.path.exists('.env'):
        print("   ❌ .env file not found")
        print("   → Run: copy .env.example .env")
        return False
    print("   ✅ .env file exists")
    
    # Check required packages
    print("\n3. Checking required packages...")
    try:
        import flask
        from flask_sqlalchemy import SQLAlchemy
        from flask_login import LoginManager
        import openai
        print("   ✅ All required packages installed")
    except ImportError as e:
        print(f"   ❌ Missing package: {str(e)}")
        print("   → Run: pip install -r requirements.txt")
        return False
    
    # Check environment variables
    print("\n4. Checking environment variables...")
    from dotenv import load_dotenv
    load_dotenv()
    
    required_vars = ['SECRET_KEY', 'OPENAI_API_KEY', 'SMTP_EMAIL', 'SMTP_PASSWORD']
    missing = []
    
    for var in required_vars:
        if not os.getenv(var) or os.getenv(var).startswith('your'):
            missing.append(var)
    
    if missing:
        print(f"   ⚠️  Please configure: {', '.join(missing)}")
        print("   → Edit .env file with your actual credentials")
    else:
        print("   ✅ All environment variables configured")
    
    # Test database connection
    print("\n5. Testing database setup...")
    try:
        from wsgi import app
        from app_factory import db
        
        with app.app_context():
            db.create_all()
        print("   ✅ Database initialized successfully")
    except Exception as e:
        print(f"   ❌ Database error: {e}")
        return False
    
    # Check if admin user exists
    print("\n6. Checking admin user...")
    try:
        from models import User
        with app.app_context():
            admin = User.query.filter_by(username='admin').first()
            if admin:
                print("   ✅ Admin user exists")
            else:
                print("   ℹ️  No admin user found")
                print("   → Create one to get started")
    except Exception as e:
        print(f"   ⚠️  {e}")
    
    print("\n" + "="*60)
    print("\n✅ Setup verification complete!")
    print("\n📋 Next steps:")
    print("   1. Ensure all environment variables are set in .env")
    print("   2. Create an admin user if you haven't")
    print("   3. Run: python wsgi.py")
    print("   4. Visit: http://localhost:5000")
    print("\n🚀 Ready to deploy? See DEPLOYMENT.md for production setup")
    
    return True

if __name__ == '__main__':
    try:
        setup_and_test()
    except KeyboardInterrupt:
        print("\n\n👋 Setup cancelled")
    except Exception as e:
        print(f"\n❌ Error: {e}")
        import traceback
        traceback.print_exc()
