# Production Deployment Script for Windows
# PowerShell script

Write-Host "🚀 Starting Birthday Reminder App Deployment..." -ForegroundColor Green

# Check if .env file exists
if (-Not (Test-Path .env)) {
    Write-Host "❌ Error: .env file not found" -ForegroundColor Red
    Write-Host "Please create .env file with required configuration"
    exit 1
}

# Create necessary directories
Write-Host "📁 Creating directories..." -ForegroundColor Cyan
New-Item -ItemType Directory -Force -Path logs, instance | Out-Null

# Install dependencies
Write-Host "📦 Installing dependencies..." -ForegroundColor Cyan
pip install -r requirements.txt

# Run database migrations
Write-Host "🗄️  Running database migrations..." -ForegroundColor Cyan
$env:FLASK_APP = "wsgi.py"
flask db init 2>$null
flask db migrate -m "Initial migration"
flask db upgrade

# Create default admin user
Write-Host "👤 Creating default admin user..." -ForegroundColor Cyan
python -c @"
from wsgi import app
from app_factory import db
from models import User

with app.app_context():
    admin = User.query.filter_by(username='admin').first()
    if not admin:
        admin = User(username='admin', email='admin@example.com')
        admin.set_password('changeme123')
        db.session.add(admin)
        db.session.commit()
        print('✅ Admin user created (username: admin, password: changeme123)')
        print('⚠️  IMPORTANT: Change the admin password after first login!')
    else:
        print('ℹ️  Admin user already exists')
"@

# Start application with Gunicorn (or use waitress for Windows)
Write-Host "🎉 Starting application..." -ForegroundColor Green
Write-Host "Note: For Windows, consider using 'waitress-serve' instead of gunicorn" -ForegroundColor Yellow
Write-Host "Install with: pip install waitress" -ForegroundColor Yellow
Write-Host "Run with: waitress-serve --port=5000 wsgi:app" -ForegroundColor Yellow

# Try to start with gunicorn (works on WSL)
gunicorn --config gunicorn_config.py wsgi:app

Write-Host "✅ Deployment complete!" -ForegroundColor Green
