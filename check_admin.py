"""Check admin user credentials"""
from wsgi import app
from models import User

with app.app_context():
    admin = User.query.filter_by(username='admin').first()
    if admin:
        print(f'✅ Admin user found')
        print(f'Username: {admin.username}')
        print(f'Email: {admin.email}')
        print(f'Password check (admin123): {admin.check_password("admin123")}')
        print(f'Password check (Admin123): {admin.check_password("Admin123")}')
        print(f'Password check (wrongpass): {admin.check_password("wrongpass")}')
    else:
        print('❌ Admin user not found')
