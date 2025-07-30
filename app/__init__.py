from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_mail import Mail
import os
import secrets

# Initialize extensions
db = SQLAlchemy()
mail = Mail()

def create_app(config_name='default'):
    """Application factory pattern"""
    # Create Flask app with correct template and static folder paths
    app = Flask(__name__, 
                template_folder='../templates',
                static_folder='../static')
    
    # Configuration
    app.config['SECRET_KEY'] = os.environ.get('SECRET_KEY', secrets.token_hex(16))
    
    # Database configuration - support both Docker and local development
    database_url = os.environ.get('DATABASE_URL')
    if database_url:
        app.config['SQLALCHEMY_DATABASE_URI'] = database_url
    else:
        # Default to local development path
        app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///instance/wedding_photos.db'
    
    app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
    app.config['UPLOAD_FOLDER'] = 'static/uploads'
    app.config['GUESTBOOK_UPLOAD_FOLDER'] = 'static/uploads/guestbook'
    app.config['MESSAGE_UPLOAD_FOLDER'] = 'static/uploads/messages'
    app.config['VIDEO_FOLDER'] = 'static/uploads/videos'
    app.config['THUMBNAIL_FOLDER'] = 'static/uploads/thumbnails'
    app.config['PHOTOBOOTH_FOLDER'] = 'static/uploads/photobooth'
    app.config['BORDER_FOLDER'] = 'static/uploads/borders'
    app.config['MAX_CONTENT_LENGTH'] = 50 * 1024 * 1024  # 50MB for videos
    app.config['ALLOWED_IMAGE_EXTENSIONS'] = {'png', 'jpg', 'jpeg', 'gif', 'webp'}
    app.config['ALLOWED_VIDEO_EXTENSIONS'] = {'mp4', 'mov', 'avi', 'webm'}
    app.config['MAX_VIDEO_DURATION'] = 15  # seconds

    # Email configuration
    app.config['MAIL_SERVER'] = os.environ.get('MAIL_SERVER', 'smtp.gmail.com')
    app.config['MAIL_PORT'] = int(os.environ.get('MAIL_PORT', 587))
    app.config['MAIL_USE_TLS'] = os.environ.get('MAIL_USE_TLS', 'True').lower() == 'true'
    app.config['MAIL_USE_SSL'] = os.environ.get('MAIL_USE_SSL', 'False').lower() == 'true'
    app.config['MAIL_USERNAME'] = os.environ.get('MAIL_USERNAME', '')
    app.config['MAIL_PASSWORD'] = os.environ.get('MAIL_PASSWORD', '')
    app.config['MAIL_DEFAULT_SENDER'] = os.environ.get('MAIL_DEFAULT_SENDER', '')

    # Initialize extensions
    db.init_app(app)
    mail.init_app(app)

    # Ensure upload directories exist
    os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)
    os.makedirs(app.config['GUESTBOOK_UPLOAD_FOLDER'], exist_ok=True)
    os.makedirs(app.config['MESSAGE_UPLOAD_FOLDER'], exist_ok=True)
    os.makedirs(app.config['VIDEO_FOLDER'], exist_ok=True)
    os.makedirs(app.config['THUMBNAIL_FOLDER'], exist_ok=True)
    os.makedirs(app.config['PHOTOBOOTH_FOLDER'], exist_ok=True)
    os.makedirs(app.config['BORDER_FOLDER'], exist_ok=True)

    # Register blueprints
    from app.views.main import main_bp
    from app.views.admin import admin_bp
    from app.views.api import api_bp
    from app.views.auth import auth_bp
    from app.views.guestbook import guestbook_bp
    from app.views.messages import messages_bp
    from app.views.photobooth import photobooth_bp
    from app.views.upload import upload_bp
    from app.views.photo_of_day import photo_of_day_bp
    from app.views.slideshow import slideshow_bp

    app.register_blueprint(main_bp)
    app.register_blueprint(admin_bp, url_prefix='/admin')
    app.register_blueprint(api_bp, url_prefix='/api')
    app.register_blueprint(auth_bp, url_prefix='/sso')
    app.register_blueprint(guestbook_bp, url_prefix='/guestbook')
    app.register_blueprint(messages_bp, url_prefix='/messages')
    app.register_blueprint(photobooth_bp, url_prefix='/photobooth')
    app.register_blueprint(upload_bp, url_prefix='/upload')
    app.register_blueprint(photo_of_day_bp)
    app.register_blueprint(slideshow_bp)

    # Register error handlers
    @app.errorhandler(413)
    def too_large(e):
        return "File is too large. Maximum size is 50MB.", 413

    @app.errorhandler(404)
    def not_found(e):
        return "Page not found.", 404

    return app 