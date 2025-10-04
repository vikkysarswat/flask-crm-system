"""Configuration settings for Flask CRM System.

Yeh file application ke saare configuration settings contain karti hai.
Different environments (development, production, testing) ke liye
alag-alag configurations provide karta hai.

"""

import os
from datetime import timedelta
from dotenv import load_dotenv


# Load environment variables from .env file
load_dotenv()


class Config:
    """Base configuration class with common settings.
    
    Yeh base class hai jisme common settings hain jo
    sabhi environments mein use hoti hain.
    """
    
    # Flask Core Settings
    SECRET_KEY = os.environ.get('SECRET_KEY') or 'dev-secret-key-change-in-production'
    
    # Database Configuration
    SQLALCHEMY_DATABASE_URI = os.environ.get('DATABASE_URL') or \
        'sqlite:///crm.db'
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    SQLALCHEMY_ECHO = False
    
    # Session Configuration
    PERMANENT_SESSION_LIFETIME = timedelta(hours=24)
    SESSION_COOKIE_SECURE = True
    SESSION_COOKIE_HTTPONLY = True
    SESSION_COOKIE_SAMESITE = 'Lax'
    
    # File Upload Settings
    MAX_CONTENT_LENGTH = 16 * 1024 * 1024  # 16MB max file size
    UPLOAD_FOLDER = os.path.join(os.path.dirname(__file__), 'uploads')
    ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg', 'gif', 'pdf', 'doc', 'docx', 
                          'xls', 'xlsx', 'txt', 'csv'}
    
    # Email Configuration (SendGrid)
    MAIL_API_KEY = os.environ.get('MAIL_API_KEY')
    MAIL_DEFAULT_SENDER = os.environ.get('MAIL_DEFAULT_SENDER') or \
        'noreply@crm.com'
    MAIL_USE_TLS = True
    MAIL_USE_SSL = False
    
    # SMS Configuration (Twilio)
    TWILIO_ACCOUNT_SID = os.environ.get('TWILIO_ACCOUNT_SID')
    TWILIO_AUTH_TOKEN = os.environ.get('TWILIO_AUTH_TOKEN')
    TWILIO_PHONE_NUMBER = os.environ.get('TWILIO_PHONE_NUMBER')
    
    # Push Notification (Firebase Cloud Messaging)
    FCM_SERVER_KEY = os.environ.get('FCM_SERVER_KEY')
    
    # Redis Configuration (for Celery and Caching)
    REDIS_URL = os.environ.get('REDIS_URL') or 'redis://localhost:6379/0'
    
    # Celery Configuration
    CELERY_BROKER_URL = REDIS_URL
    CELERY_RESULT_BACKEND = REDIS_URL
    CELERY_ACCEPT_CONTENT = ['json']
    CELERY_TASK_SERIALIZER = 'json'
    CELERY_RESULT_SERIALIZER = 'json'
    CELERY_TIMEZONE = 'Asia/Kolkata'
    
    # SocketIO Configuration
    SOCKETIO_MESSAGE_QUEUE = REDIS_URL
    SOCKETIO_ASYNC_MODE = 'eventlet'
    
    # Application Settings
    APP_NAME = os.environ.get('APP_NAME') or 'CRM System'
    APP_URL = os.environ.get('APP_URL') or 'http://localhost:5000'
    ITEMS_PER_PAGE = 20
    
    # Security Settings
    WTF_CSRF_ENABLED = True
    WTF_CSRF_TIME_LIMIT = None
    
    # Lead Scoring Configuration
    LEAD_SCORE_EMAIL_OPENED = 5
    LEAD_SCORE_LINK_CLICKED = 10
    LEAD_SCORE_FORM_SUBMITTED = 15
    LEAD_SCORE_PAGE_VISITED = 3
    LEAD_SCORE_DEMO_REQUESTED = 50
    
    # Activity Settings
    ACTIVITY_RETENTION_DAYS = 365  # Keep activities for 1 year
    
    # API Rate Limiting
    RATELIMIT_ENABLED = True
    RATELIMIT_DEFAULT = "200 per day;50 per hour"
    RATELIMIT_STORAGE_URL = REDIS_URL


class DevelopmentConfig(Config):
    """Development environment configuration.
    
    Development ke liye special settings jaise debug mode
    aur detailed error messages.
    """
    
    DEBUG = True
    TESTING = False
    SQLALCHEMY_ECHO = True  # SQL queries ko print karega
    SESSION_COOKIE_SECURE = False  # HTTP pe bhi kaam karega


class ProductionConfig(Config):
    """Production environment configuration.
    
    Production ke liye secure aur optimized settings.
    """
    
    DEBUG = False
    TESTING = False
    
    # Production mein strong secret key mandatory hai
    if not os.environ.get('SECRET_KEY'):
        raise ValueError("SECRET_KEY environment variable must be set in production!")
    
    # SSL/TLS enforcement
    SESSION_COOKIE_SECURE = True
    PREFERRED_URL_SCHEME = 'https'
    
    # PostgreSQL is recommended for production
    if 'sqlite' in Config.SQLALCHEMY_DATABASE_URI:
        print("WARNING: Using SQLite in production is not recommended!")


class TestingConfig(Config):
    """Testing environment configuration.
    
    Unit tests aur integration tests ke liye settings.
    """
    
    TESTING = True
    DEBUG = True
    SQLALCHEMY_DATABASE_URI = 'sqlite:///test.db'
    WTF_CSRF_ENABLED = False
    RATELIMIT_ENABLED = False


# Configuration dictionary for easy access
config = {
    'development': DevelopmentConfig,
    'production': ProductionConfig,
    'testing': TestingConfig,
    'default': DevelopmentConfig
}


def get_config(env=None):
    """Get configuration object based on environment.
    
    Args:
        env (str): Environment name (development/production/testing)
        
    Returns:
        Config: Configuration class instance
        
    Example:
        >>> config = get_config('production')
        >>> print(config.DEBUG)
        False
    """
    if env is None:
        env = os.environ.get('FLASK_ENV', 'development')
    
    return config.get(env, config['default'])
