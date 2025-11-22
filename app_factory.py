from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager
from flask_migrate import Migrate
from flask_limiter import Limiter
from flask_limiter.util import get_remote_address
from flask_wtf.csrf import CSRFProtect
import logging
from logging.handlers import RotatingFileHandler
import os
from dotenv import load_dotenv

load_dotenv()

# Initialize extensions
db = SQLAlchemy()
login_manager = LoginManager()
migrate = Migrate()
limiter = Limiter(
    key_func=get_remote_address,
    default_limits=["200 per day", "50 per hour"]
)
csrf = CSRFProtect()

def create_app(config_name='development'):
    """Application factory pattern"""
    app = Flask(__name__)
    
    # Load configuration
    from config import config
    app.config.from_object(config[config_name])
    
    # Initialize extensions
    db.init_app(app)
    login_manager.init_app(app)
    migrate.init_app(app, db)
    limiter.init_app(app)
    csrf.init_app(app)
    
    # Login configuration
    login_manager.login_view = 'auth.login'
    login_manager.login_message = 'Please log in to access this page.'
    login_manager.login_message_category = 'info'
    
    # Setup logging
    setup_logging(app)
    
    # Register blueprints
    from routes import main_bp, auth_bp, api_bp
    app.register_blueprint(main_bp)
    app.register_blueprint(auth_bp, url_prefix='/auth')
    app.register_blueprint(api_bp, url_prefix='/api')
    
    # Register error handlers
    register_error_handlers(app)
    
    # Create database tables
    with app.app_context():
        db.create_all()
    
    # Start background scheduler
    if not app.config.get('TESTING'):
        start_scheduler(app)
    
    return app


def setup_logging(app):
    """Configure application logging"""
    if not app.debug and not app.testing:
        # Create logs directory if it doesn't exist
        if not os.path.exists('logs'):
            os.mkdir('logs')
        
        # File handler
        file_handler = RotatingFileHandler(
            'logs/birthday_app.log',
            maxBytes=10240000,  # 10MB
            backupCount=10
        )
        file_handler.setFormatter(logging.Formatter(
            '%(asctime)s %(levelname)s: %(message)s [in %(pathname)s:%(lineno)d]'
        ))
        file_handler.setLevel(logging.INFO)
        app.logger.addHandler(file_handler)
        
        app.logger.setLevel(logging.INFO)
        app.logger.info('Birthday App startup')


def register_error_handlers(app):
    """Register error handlers"""
    
    @app.errorhandler(404)
    def not_found_error(error):
        return {'error': 'Resource not found'}, 404
    
    @app.errorhandler(500)
    def internal_error(error):
        db.session.rollback()
        app.logger.error(f'Server Error: {error}')
        return {'error': 'Internal server error'}, 500
    
    @app.errorhandler(429)
    def ratelimit_handler(error):
        return {'error': 'Rate limit exceeded. Please try again later.'}, 429


def start_scheduler(app):
    """Start background scheduler for birthday checks"""
    from apscheduler.schedulers.background import BackgroundScheduler
    from services import check_birthdays
    
    scheduler = BackgroundScheduler()
    
    # Check birthdays every hour
    scheduler.add_job(
        func=lambda: check_birthdays(app),
        trigger="interval",
        hours=1,
        id='hourly_birthday_check'
    )
    
    # Check at midnight daily
    scheduler.add_job(
        func=lambda: check_birthdays(app),
        trigger="cron",
        hour=0,
        minute=0,
        id='midnight_birthday_check'
    )
    
    scheduler.start()
    app.logger.info('Background scheduler started')
    
    # Shutdown scheduler when app stops
    import atexit
    atexit.register(lambda: scheduler.shutdown())
