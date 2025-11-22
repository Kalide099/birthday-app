# Birthday Reminder App 🎂

A **production-ready**, intelligent birthday reminder application that helps you never forget your friends' birthdays! The app uses AI to generate personalized birthday messages and automatically sends them via email.

## ✨ Features

### Core Features
- 📅 **Save Birthday Dates** - Store friends' birthdays with detailed information
- 🔔 **Smart Alerts** - Automated notifications one day before birthdays
- 🤖 **AI-Generated Messages** - Personalized wishes powered by OpenAI
- ✉️ **Email Automation** - Messages automatically sent at midnight
- 📊 **Upcoming Birthdays** - Dashboard showing next 30 days
- 🎨 **Beautiful UI** - Modern, responsive design

### Professional Features
- 👥 **Multi-User Support** - Secure user authentication system
- 🔒 **Enterprise Security** - CSRF protection, rate limiting, secure sessions
- 🚀 **Production Ready** - Gunicorn WSGI server, Docker support
- 📝 **Comprehensive Logging** - Rotating logs with error tracking
- 🗄️ **Database Migrations** - Version-controlled schema management
- 🔄 **RESTful API** - Well-documented endpoints
- 🐳 **Docker Support** - Containerized deployment
- ⚡ **Performance Optimized** - Indexed queries, efficient architecture

## 🛠️ Technology Stack

### Backend
- **Framework**: Flask 3.0
- **Database**: SQLAlchemy with SQLite (PostgreSQL/MySQL compatible)
- **Authentication**: Flask-Login with secure password hashing
- **Migrations**: Flask-Migrate (Alembic)
- **WSGI Server**: Gunicorn (production)
- **AI**: OpenAI GPT-3.5-Turbo
- **Scheduler**: APScheduler for background tasks
- **Security**: Flask-WTF (CSRF), Flask-Limiter (rate limiting)

### Frontend
- **HTML5, CSS3, JavaScript**
- **Font Awesome Icons**
- **Responsive Design**

### DevOps
- **Docker & Docker Compose**
- **Deployment scripts for multiple platforms**
- **Logging with rotation**
- **Health checks**

## Prerequisites 📋

- Python 3.8 or higher
- OpenAI API Key ([Get one here](https://platform.openai.com/api-keys))

## 🚀 Quick Start

### Development Setup

1. **Clone the repository**
   ```powershell
   git clone <your-repo-url>
   cd Projects1
   ```

2. **Create virtual environment**
   ```powershell
   python -m venv venv
   .\venv\Scripts\Activate.ps1
   ```

3. **Install dependencies**
   ```powershell
   pip install -r requirements.txt
   ```

4. **Configure environment**
   ```powershell
   copy .env.example .env
   # Edit .env with your credentials
   ```

5. **Initialize database**
   ```powershell
   $env:FLASK_APP="wsgi.py"
   flask db init
   flask db migrate -m "Initial migration"
   flask db upgrade
   ```

6. **Create admin user**
   ```powershell
   python -c "from wsgi import app; from app_factory import db; from models import User; app.app_context().push(); admin = User(username='admin', email='admin@example.com'); admin.set_password('yourpassword'); db.session.add(admin); db.session.commit(); print('Admin created')"
   ```

7. **Run application**
   ```powershell
   python wsgi.py
   ```

8. **Access the app**
   - Open http://localhost:5000
   - Login with your admin credentials
   - Start adding friends!

### Production Deployment

See [DEPLOYMENT.md](DEPLOYMENT.md) for detailed production deployment instructions including:
- Traditional server deployment (Gunicorn/Waitress)
- Docker deployment
- Cloud platform deployment (Heroku, AWS, DigitalOcean)
- Security configuration
- Monitoring and maintenance

## How It Works 🔄

### Birthday Checking
The app uses APScheduler to run checks:
- Every hour during the day
- At midnight (00:00) daily for birthday messages

### Alert System
- **Reminder Alert**: Created one day before the birthday
- **Birthday Alert**: Created on the birthday day with the AI-generated message

### AI Message Generation
The app uses OpenAI's GPT-3.5-Turbo to generate personalized birthday messages based on:
- Friend's name
- Your relationship with them
- Creative and heartfelt templates

## Project Structure 📁

```
Projects1/
├── app.py                 # Main Flask application
├── templates/
│   └── index.html        # Frontend HTML
├── static/
│   ├── style.css         # Styling
│   └── script.js         # Frontend JavaScript
├── requirements.txt      # Python dependencies
├── .env.example          # Environment variables template
├── .env                  # Your actual environment variables (create this)
├── birthdays.db          # SQLite database (created automatically)
└── README.md             # This file
```

## API Endpoints 🔌

- `GET /` - Main page
- `GET /api/friends` - Get all friends
- `POST /api/friends` - Add a new friend
- `PUT /api/friends/<id>` - Update a friend
- `DELETE /api/friends/<id>` - Delete a friend
- `GET /api/alerts` - Get all alerts
- `PUT /api/alerts/<id>/read` - Mark alert as read
- `GET /api/messages/<friend_id>` - Get messages for a friend
- `GET /api/upcoming-birthdays` - Get upcoming birthdays (next 30 days)

## Database Schema 📊

### Friend Table
- id, name, birthday, email, phone, relationship, created_at

### BirthdayMessage Table
- id, friend_id, message, sent_at, year

### Alert Table
- id, friend_id, alert_type, message, created_at, is_read

## Customization 🎨

### Change Alert Frequency
Edit `app.py` line ~200:
```python
# Check every 30 minutes instead of every hour
scheduler.add_job(func=check_birthdays, trigger="interval", minutes=30)
```

### Customize AI Messages
Edit the `generate_birthday_message()` function in `app.py` to modify the prompt sent to OpenAI.

### Change UI Colors
Edit `static/style.css` to customize the color scheme:
```css
background: linear-gradient(135deg, #your-color-1 0%, #your-color-2 100%);
```

## Troubleshooting 🔧

**Issue**: "OpenAI API key not found"
- **Solution**: Make sure you created a `.env` file with your API key

**Issue**: Database errors
- **Solution**: Delete `birthdays.db` and restart the app to create a fresh database

**Issue**: Scheduler not running
- **Solution**: Make sure you're not running in debug mode with reloader (app already handles this)

**Issue**: No alerts appearing
- **Solution**: Check that birthdays are set correctly and wait for the scheduler to run

## Security Notes 🔒

- Never commit your `.env` file to version control
- Keep your OpenAI API key secret
- Change the SECRET_KEY in production
- The app stores data locally in SQLite

## Future Enhancements 💡

Potential improvements you could add:
- Email/SMS integration for sending actual messages
- Multiple notification methods (desktop notifications, Telegram, WhatsApp)
- Import birthdays from contacts
- Birthday gift suggestions
- Birthday countdown widgets
- Multi-user support with authentication
- Calendar integration

## License 📄

This project is free to use and modify for personal and commercial purposes.

## Support 💬

For issues or questions, please check the code comments or modify the application to suit your needs.

## Credits 🙏

- OpenAI for GPT API
- Flask framework
- Font Awesome for icons

---

**Made with ❤️ for never forgetting important birthdays!**
