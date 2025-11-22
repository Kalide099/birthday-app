#!/bin/bash

# Production Deployment Script for Birthday Reminder App

echo "🚀 Starting Birthday Reminder App Deployment..."

# Check if .env file exists
if [ ! -f .env ]; then
    echo "❌ Error: .env file not found"
    echo "Please create .env file with required configuration"
    exit 1
fi

# Create necessary directories
echo "📁 Creating directories..."
mkdir -p logs instance

# Install dependencies
echo "📦 Installing dependencies..."
pip install -r requirements.txt

# Run database migrations
echo "🗄️  Running database migrations..."
export FLASK_APP=wsgi.py
flask db init 2>/dev/null || true
flask db migrate -m "Initial migration"
flask db upgrade

# Create default admin user (optional)
echo "👤 Creating default admin user..."
python -c "
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
"

# Start application with Gunicorn
echo "🎉 Starting application with Gunicorn..."
gunicorn --config gunicorn_config.py wsgi:app

echo "✅ Deployment complete!"
