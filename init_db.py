"""
Initialize database for production deployment
Run this after deploying to create tables and admin user
"""
from wsgi import app
from app_factory import db
from models import User
import os

def init_db():
    """Initialize database and create admin user"""
    with app.app_context():
        # Create all tables
        db.create_all()
        print('✅ Database tables created!')
        
        # Check if admin exists
        admin = User.query.filter_by(username='admin').first()
        if not admin:
            admin = User(username='admin', email=os.getenv('ADMIN_EMAIL', 'admin@birthday.com'))
            admin.set_password(os.getenv('ADMIN_PASSWORD', 'admin123'))
            db.session.add(admin)
            db.session.commit()
            print('✅ Admin user created!')
            print(f'   Username: admin')
            print(f'   Password: {os.getenv("ADMIN_PASSWORD", "admin123")}')
            print('   ⚠️  CHANGE THIS PASSWORD IMMEDIATELY!')
        else:
            print('ℹ️  Admin user already exists')

if __name__ == '__main__':
    init_db()
