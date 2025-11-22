"""
Main application entry point
"""
from app_factory import create_app
import os

# Get configuration from environment
config_name = os.getenv('FLASK_ENV', 'development')
app = create_app(config_name)

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)
