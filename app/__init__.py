"""Flask application factory.

Yeh file Flask application ko initialize karta hai aur
saare extensions, blueprints aur configurations setup karta hai.

"""

from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager
from flask_migrate import Migrate
from flask_socketio import SocketIO
from flask_mail import Mail
from celery import Celery
import logging
from logging.handlers import RotatingFileHandler
import os

from config import get_config


# Initialize extensions
db = SQLAlchemy()
login_manager = LoginManager()
migrate = Migrate()
socketio = SocketIO()
mail = Mail()
celery = Celery(__name__)


def create_app(env=None):
    """Application factory function.
    
    Flask application ko create aur configure karta hai.
    
    Args:
        env (str): Environment name (development/production/testing)
        
    Returns:
        Flask: Configured Flask application instance
        
    Example:
        >>> app = create_app('production')
        >>> app.run()
    """
    app = Flask(__name__)
    
    # Load configuration
    config_class = get_config(env)
    app.config.from_object(config_class)
    
    # Initialize extensions with app
    initialize_extensions(app)
    
    # Register blueprints
    register_blueprints(app)
    
    # Setup logging
    setup_logging(app)
    
    # Register error handlers
    register_error_handlers(app)
    
    # Context processors
    register_context_processors(app)
    
    return app


def initialize_extensions(app):
    """Initialize Flask extensions.
    
    Saare Flask extensions ko app ke saath initialize karta hai.
    
    Args:
        app (Flask): Flask application instance
    """
    # Database
    db.init_app(app)
    
    # Migrations
    migrate.init_app(app, db)
    
    # Login Manager
    login_manager.init_app(app)
    login_manager.login_view = 'auth.login'
    login_manager.login_message = 'Please login to access this page.'
    login_manager.login_message_category = 'info'
    
    # SocketIO for real-time features
    socketio.init_app(
        app,
        message_queue=app.config['SOCKETIO_MESSAGE_QUEUE'],
        async_mode=app.config['SOCKETIO_ASYNC_MODE'],
        cors_allowed_origins="*"
    )
    
    # Mail
    mail.init_app(app)
    
    # Celery for background tasks
    celery.conf.update(app.config)
    
    # Create upload folder if not exists
    os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)


def register_blueprints(app):
    """Register application blueprints.
    
    Saare route blueprints ko app ke saath register karta hai.
    Yeh modular structure provide karta hai.
    
    Args:
        app (Flask): Flask application instance
    """
    from app.routes.auth import auth_bp
    from app.routes.main import main_bp
    from app.routes.contacts import contacts_bp
    from app.routes.leads import leads_bp
    from app.routes.deals import deals_bp
    from app.routes.activities import activities_bp
    from app.routes.communications import communications_bp
    from app.routes.reports import reports_bp
    from app.routes.settings import settings_bp
    from app.routes.api import api_bp
    
    app.register_blueprint(auth_bp)
    app.register_blueprint(main_bp)
    app.register_blueprint(contacts_bp)
    app.register_blueprint(leads_bp)
    app.register_blueprint(deals_bp)
    app.register_blueprint(activities_bp)
    app.register_blueprint(communications_bp)
    app.register_blueprint(reports_bp)
    app.register_blueprint(settings_bp)
    app.register_blueprint(api_bp)


def setup_logging(app):
    """Setup application logging.
    
    Production environment ke liye file-based logging configure karta hai.
    
    Args:
        app (Flask): Flask application instance
    """
    if not app.debug and not app.testing:
        # Create logs directory
        if not os.path.exists('logs'):
            os.mkdir('logs')
        
        # File handler for application logs
        file_handler = RotatingFileHandler(
            'logs/crm.log',
            maxBytes=10240000,  # 10MB
            backupCount=10
        )
        file_handler.setFormatter(logging.Formatter(
            '%(asctime)s %(levelname)s: %(message)s '
            '[in %(pathname)s:%(lineno)d]'
        ))
        file_handler.setLevel(logging.INFO)
        app.logger.addHandler(file_handler)
        
        app.logger.setLevel(logging.INFO)
        app.logger.info('CRM System startup')


def register_error_handlers(app):
    """Register custom error handlers.
    
    Different HTTP errors ke liye custom error pages register karta hai.
    
    Args:
        app (Flask): Flask application instance
    """
    from flask import render_template
    
    @app.errorhandler(404)
    def not_found_error(error):
        """Handle 404 errors."""
        return render_template('errors/404.html'), 404
    
    @app.errorhandler(500)
    def internal_error(error):
        """Handle 500 errors."""
        db.session.rollback()
        return render_template('errors/500.html'), 500
    
    @app.errorhandler(403)
    def forbidden_error(error):
        """Handle 403 errors."""
        return render_template('errors/403.html'), 403


def register_context_processors(app):
    """Register template context processors.
    
    Template mein globally available variables add karta hai.
    
    Args:
        app (Flask): Flask application instance
    """
    from datetime import datetime
    
    @app.context_processor
    def utility_processor():
        """Add utility functions to template context."""
        return {
            'app_name': app.config['APP_NAME'],
            'current_year': datetime.now().year
        }


@login_manager.user_loader
def load_user(user_id):
    """Load user for Flask-Login.
    
    User ID se user object ko load karta hai.
    
    Args:
        user_id (int): User database ID
        
    Returns:
        User: User object or None
    """
    from app.models.user import User
    return User.query.get(int(user_id))
