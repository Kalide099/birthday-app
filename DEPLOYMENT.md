# 🚀 Professional Deployment Guide

## Production-Ready Features

### ✅ What's New:

1. **User Authentication** 
   - Multi-user support with Flask-Login
   - Secure password hashing
   - User registration and login system
   - Session management

2. **Security Enhancements**
   - CSRF protection
   - Rate limiting (prevents abuse)
   - Secure session cookies
   - SQL injection protection
   - XSS prevention

3. **Production Server**
   - Gunicorn WSGI server
   - Multi-worker support
   - Production-grade configuration
   - Docker support

4. **Database Management**
   - Flask-Migrate for version control
   - Automatic migrations
   - Database relationships and indexes

5. **Logging & Monitoring**
   - Rotating file logs
   - Error tracking
   - Request logging
   - Health checks

6. **Code Organization**
   - Application factory pattern
   - Blueprints for modularity
   - Separate configuration files
   - Service layer architecture

---

## 📋 Prerequisites

- Python 3.8+
- pip
- Virtual environment (recommended)
- OpenAI API key
- Email SMTP credentials
- (Optional) Docker

---

## 🔧 Local Development Setup

### 1. Install Dependencies

```powershell
# Create virtual environment
python -m venv venv
.\venv\Scripts\Activate.ps1

# Install packages
pip install -r requirements.txt
```

### 2. Configure Environment

Copy `.env.example` to `.env` and fill in:

```env
FLASK_ENV=development
SECRET_KEY=your-random-secret-key-here
DATABASE_URL=sqlite:///birthdays.db

OPENAI_API_KEY=your-openai-api-key
SMTP_SERVER=smtp.gmail.com
SMTP_PORT=587
SMTP_EMAIL=your-email@gmail.com
SMTP_PASSWORD=your-app-password
```

### 3. Initialize Database

```powershell
$env:FLASK_APP="wsgi.py"
flask db init
flask db migrate -m "Initial migration"
flask db upgrade
```

### 4. Create Admin User

```powershell
python -c "from wsgi import app; from app_factory import db; from models import User; app.app_context().push(); admin = User(username='admin', email='admin@example.com'); admin.set_password('yourpassword'); db.session.add(admin); db.session.commit(); print('Admin created')"
```

### 5. Run Development Server

```powershell
python wsgi.py
```

Visit: http://localhost:5000

---

## 🚀 Production Deployment

### Option 1: Traditional Server

#### Using Gunicorn (Linux/Mac/WSL)

```bash
# Run deployment script
chmod +x deploy.sh
./deploy.sh
```

Or manually:

```bash
gunicorn --config gunicorn_config.py wsgi:app
```

#### Using Waitress (Windows)

```powershell
pip install waitress
waitress-serve --port=5000 --threads=4 wsgi:app
```

### Option 2: Docker Deployment

#### Build and Run

```powershell
# Build image
docker build -t birthday-app .

# Run container
docker run -d -p 5000:5000 --env-file .env --name birthday-app birthday-app
```

#### Using Docker Compose

```powershell
docker-compose up -d
```

#### Docker Commands

```powershell
# View logs
docker-compose logs -f

# Stop
docker-compose down

# Restart
docker-compose restart
```

---

## 🌐 Deployment Platforms

### Heroku

1. Create `Procfile`:
```
web: gunicorn --config gunicorn_config.py wsgi:app
```

2. Deploy:
```bash
heroku create your-app-name
git push heroku main
heroku config:set SECRET_KEY=your-key
heroku config:set OPENAI_API_KEY=your-key
```

### AWS EC2

1. SSH into instance
2. Clone repository
3. Run deployment script
4. Set up Nginx reverse proxy
5. Configure systemd service

### DigitalOcean

1. Create droplet
2. Install dependencies
3. Run deployment script
4. Configure firewall
5. Set up SSL with Let's Encrypt

### Railway/Render

1. Connect GitHub repository
2. Set environment variables
3. Deploy automatically

---

## 🔒 Security Checklist

- [ ] Change SECRET_KEY to random strong value
- [ ] Use HTTPS in production
- [ ] Set SESSION_COOKIE_SECURE=True with HTTPS
- [ ] Keep dependencies updated
- [ ] Use strong admin password
- [ ] Enable firewall
- [ ] Regular backups
- [ ] Monitor logs
- [ ] Rate limiting enabled
- [ ] CSRF protection enabled

---

## 📊 Monitoring

### View Logs

```powershell
# Application logs
Get-Content logs/birthday_app.log -Tail 100 -Wait

# Gunicorn logs
Get-Content logs/gunicorn_error.log -Tail 100 -Wait
```

### Health Check

```powershell
curl http://localhost:5000/
```

---

## 🔄 Updates & Maintenance

### Update Code

```bash
git pull origin main
pip install -r requirements.txt
flask db migrate -m "Update description"
flask db upgrade
# Restart application
```

### Backup Database

```powershell
# Copy database file
Copy-Item instance/birthdays.db instance/birthdays_backup_$(Get-Date -Format "yyyyMMdd").db
```

---

## ⚙️ Configuration

### Environment Variables

| Variable | Description | Required |
|----------|-------------|----------|
| `FLASK_ENV` | Environment (development/production) | Yes |
| `SECRET_KEY` | Flask secret key | Yes |
| `DATABASE_URL` | Database connection string | Yes |
| `OPENAI_API_KEY` | OpenAI API key for AI messages | Yes |
| `SMTP_SERVER` | Email server address | Yes |
| `SMTP_PORT` | Email server port | Yes |
| `SMTP_EMAIL` | Sender email address | Yes |
| `SMTP_PASSWORD` | Email password/app password | Yes |

### Gunicorn Configuration

Edit `gunicorn_config.py` to adjust:
- Number of workers
- Timeout settings
- Logging configuration
- Binding address

---

## 🧪 Testing

### Run Tests

```powershell
$env:FLASK_ENV="testing"
python -m pytest tests/
```

---

## 🐛 Troubleshooting

### Database Errors

```powershell
# Reset database
Remove-Item instance/birthdays.db
flask db upgrade
```

### Port Already in Use

```powershell
# Find process
netstat -ano | findstr :5000

# Kill process
taskkill /PID <process_id> /F
```

### Email Not Sending

- Verify SMTP credentials
- Check firewall rules
- Use app password for Gmail
- Enable less secure apps (if needed)

---

## 📚 API Documentation

### Authentication Endpoints

- `POST /auth/register` - Register new user
- `POST /auth/login` - User login
- `GET /auth/logout` - User logout

### API Endpoints

- `GET /api/friends` - Get all friends
- `POST /api/friends` - Add friend
- `PUT /api/friends/<id>` - Update friend
- `DELETE /api/friends/<id>` - Delete friend
- `GET /api/alerts` - Get alerts
- `PUT /api/alerts/<id>/read` - Mark alert as read
- `GET /api/messages/<friend_id>` - Get messages for friend
- `GET /api/upcoming-birthdays` - Get upcoming birthdays

---

## 📞 Support

For issues or questions:
1. Check logs in `logs/` directory
2. Review configuration in `.env`
3. Consult this documentation
4. Check application logs

---

## 🎯 Performance Tips

1. **Database Optimization**
   - Indexes are already set up
   - Use pagination for large datasets
   - Regular vacuum/optimize

2. **Caching**
   - Consider Redis for session storage
   - Cache frequent queries

3. **Workers**
   - Adjust Gunicorn workers based on CPU cores
   - Formula: (2 x CPU cores) + 1

4. **Monitoring**
   - Set up log rotation
   - Monitor disk space
   - Track response times

---

**Your Birthday Reminder App is now production-ready! 🎉**
