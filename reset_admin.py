"""Reset admin password"""
from wsgi import app
from app_factory import db
from models import User

with app.app_context():
    # Delete existing admin
    admin = User.query.filter_by(username='admin').first()
    if admin:
        db.session.delete(admin)
        db.session.commit()
        print('✅ Deleted old admin user')
    
    # Create new admin
    admin = User(username='admin', email='admin@birthday.com')
    admin.set_password('admin123')
    db.session.add(admin)
    db.session.commit()
    
    print('✅ New admin user created!')
    print('   Username: admin')
    print('   Password: admin123')
    print()
    
    # Verify it works
    test = User.query.filter_by(username='admin').first()
    print(f'✅ Verification - Password check: {test.check_password("admin123")}')
