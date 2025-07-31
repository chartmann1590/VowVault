from flask import Flask, render_template, request, redirect, url_for, jsonify, make_response, send_file, send_from_directory, session
from flask_sqlalchemy import SQLAlchemy
from flask_mail import Mail, Message
from datetime import datetime, date
import os
from werkzeug.utils import secure_filename
import secrets
import qrcode
from io import BytesIO
from reportlab.lib.pagesizes import letter, A4
from reportlab.lib import colors
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Image, Table, TableStyle
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import inch
from reportlab.lib.enums import TA_CENTER, TA_JUSTIFY
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
import json
import subprocess
import tempfile
import base64
from PIL import Image as PILImage
import zipfile
import shutil
import email
import imaplib
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from email.mime.image import MIMEImage
from email.mime.base import MIMEBase
from email import encoders
import threading
import time
import requests
from pathlib import Path
import sqlite3

# Import PhotoOfDayCandidate for automatic candidate functionality
from app.models.photo_of_day import PhotoOfDayCandidate

# Import database optimization utilities
from app.utils.db_optimization import db_optimizer, optimize_photo_queries, get_photo_stats, maintenance_task

# Import system logging utilities
from app.utils.system_logger import log_system_event, log_info, log_error, log_exception, log_critical

app = Flask(__name__)
app.config['SECRET_KEY'] = os.environ.get('SECRET_KEY', secrets.token_hex(16))
app.config['SQLALCHEMY_DATABASE_URI'] = os.environ.get('DATABASE_URL', 'sqlite:///wedding_photos.db')
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['UPLOAD_FOLDER'] = 'static/uploads'
app.config['GUESTBOOK_UPLOAD_FOLDER'] = 'static/uploads/guestbook'
app.config['MESSAGE_UPLOAD_FOLDER'] = 'static/uploads/messages'
app.config['VIDEO_FOLDER'] = 'static/uploads/videos'
app.config['THUMBNAIL_FOLDER'] = 'static/uploads/thumbnails'
app.config['PHOTOBOOTH_FOLDER'] = 'static/uploads/photobooth'
app.config['BORDER_FOLDER'] = 'static/uploads/borders'
app.config['MAX_CONTENT_LENGTH'] = 50 * 1024 * 1024  # Increased to 50MB for videos
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

db = SQLAlchemy(app)
mail = Mail(app)

# Initialize database optimizer
db_optimizer.init_app(app)

# Jinja2 filter for timezone formatting
@app.template_filter('timezone_format')
def timezone_format(dt, format_str='%B %d, %Y at %I:%M %p'):
    """Format datetime in admin's selected timezone"""
    from app.utils.settings_utils import format_datetime_in_timezone
    return format_datetime_in_timezone(dt, format_str)

# Ensure upload directories exist
os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)
os.makedirs(app.config['GUESTBOOK_UPLOAD_FOLDER'], exist_ok=True)
os.makedirs(app.config['MESSAGE_UPLOAD_FOLDER'], exist_ok=True)
os.makedirs(app.config['VIDEO_FOLDER'], exist_ok=True)
os.makedirs(app.config['THUMBNAIL_FOLDER'], exist_ok=True)
os.makedirs(app.config['PHOTOBOOTH_FOLDER'], exist_ok=True)
os.makedirs(app.config['BORDER_FOLDER'], exist_ok=True)

# Database Models
class Photo(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    filename = db.Column(db.String(255), nullable=False)
    original_filename = db.Column(db.String(255), nullable=False)
    uploader_name = db.Column(db.String(100), default='Anonymous')
    uploader_identifier = db.Column(db.String(100))  # Track who uploaded the photo
    upload_date = db.Column(db.DateTime, default=datetime.utcnow)
    description = db.Column(db.Text)
    tags = db.Column(db.Text)  # Comma-separated tags
    likes = db.Column(db.Integer, default=0)
    media_type = db.Column(db.String(10), default='image')  # 'image' or 'video'
    thumbnail_filename = db.Column(db.String(255))  # For video thumbnails
    duration = db.Column(db.Float)  # Video duration in seconds
    is_photobooth = db.Column(db.Boolean, default=False)  # Track photobooth photos
    comments = db.relationship('Comment', backref='photo', lazy=True, cascade='all, delete-orphan')

class Comment(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    photo_id = db.Column(db.Integer, db.ForeignKey('photo.id'), nullable=False)
    commenter_name = db.Column(db.String(100), default='Anonymous')
    content = db.Column(db.Text, nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

class Like(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    photo_id = db.Column(db.Integer, db.ForeignKey('photo.id'), nullable=False)
    user_identifier = db.Column(db.String(100), nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

class GuestbookEntry(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    message = db.Column(db.Text, nullable=False)
    location = db.Column(db.String(100))
    photo_filename = db.Column(db.String(255))
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

# New Message Board Models
class Message(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    author_name = db.Column(db.String(100), nullable=False, default='Anonymous')
    author_identifier = db.Column(db.String(100))  # Track who posted the message
    content = db.Column(db.Text, nullable=False)
    photo_filename = db.Column(db.String(255))
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    likes = db.Column(db.Integer, default=0)
    is_hidden = db.Column(db.Boolean, default=False)
    message_comments = db.relationship('MessageComment', backref='message', lazy=True, cascade='all, delete-orphan')

class MessageComment(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    message_id = db.Column(db.Integer, db.ForeignKey('message.id'), nullable=False)
    commenter_name = db.Column(db.String(100), default='Anonymous')
    content = db.Column(db.Text, nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    is_hidden = db.Column(db.Boolean, default=False)

class MessageLike(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    message_id = db.Column(db.Integer, db.ForeignKey('message.id'), nullable=False)
    user_identifier = db.Column(db.String(100), nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

class Settings(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    key = db.Column(db.String(50), unique=True, nullable=False)
    value = db.Column(db.Text)
    
    @staticmethod
    def get(key, default=None):
        setting = Settings.query.filter_by(key=key).first()
        return setting.value if setting else default
    
    @staticmethod
    def set(key, value):
        setting = Settings.query.filter_by(key=key).first()
        if setting:
            setting.value = value
        else:
            setting = Settings(key=key, value=value)
            db.session.add(setting)
        db.session.commit()

class EmailLog(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    sender_email = db.Column(db.String(255), nullable=False)
    subject = db.Column(db.String(255))
    received_at = db.Column(db.DateTime, default=datetime.utcnow)
    processed_at = db.Column(db.DateTime)
    status = db.Column(db.String(50), nullable=False)  # 'success', 'rejected', 'error'
    photo_count = db.Column(db.Integer, default=0)
    error_message = db.Column(db.Text)
    response_sent = db.Column(db.Boolean, default=False)
    response_type = db.Column(db.String(50))  # 'confirmation', 'rejection'

class ImmichSyncLog(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    filename = db.Column(db.String(255), nullable=False)
    file_path = db.Column(db.String(500), nullable=False)
    sync_date = db.Column(db.DateTime, default=datetime.utcnow)
    status = db.Column(db.String(50), nullable=False)  # 'success', 'error', 'pending'
    immich_asset_id = db.Column(db.String(255))  # Immich asset ID if successful
    error_message = db.Column(db.Text)
    retry_count = db.Column(db.Integer, default=0)
    last_retry = db.Column(db.DateTime)

class NotificationUser(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_identifier = db.Column(db.String(100), unique=True, nullable=False)
    user_name = db.Column(db.String(100), default='Anonymous')
    notifications_enabled = db.Column(db.Boolean, default=True)
    last_seen = db.Column(db.DateTime, default=datetime.utcnow)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    device_info = db.Column(db.Text)  # Store browser/device information

class Notification(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_identifier = db.Column(db.String(100), nullable=False)
    title = db.Column(db.String(255), nullable=False)
    message = db.Column(db.Text, nullable=False)
    notification_type = db.Column(db.String(50), default='admin')  # 'admin', 'like', 'comment'
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    read_at = db.Column(db.DateTime)  # When user saw the notification
    is_read = db.Column(db.Boolean, default=False)
    # Navigation fields
    content_type = db.Column(db.String(50))  # 'photo', 'message', 'admin'
    content_id = db.Column(db.Integer)  # ID of the photo, message, etc.

def allowed_file(filename):
    """Check if file extension is allowed"""
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in (app.config['ALLOWED_IMAGE_EXTENSIONS'] | app.config['ALLOWED_VIDEO_EXTENSIONS'])

def is_video(filename):
    """Check if file is a video"""
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in app.config['ALLOWED_VIDEO_EXTENSIONS']

def is_image(filename):
    """Check if file is an image"""
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in app.config['ALLOWED_IMAGE_EXTENSIONS']

def get_video_duration(filepath):
    """Get video duration using ffprobe"""
    try:
        cmd = [
            'ffprobe', '-v', 'error', '-show_entries',
            'format=duration', '-of', 'default=noprint_wrappers=1:nokey=1',
            filepath
        ]
        result = subprocess.run(cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)
        if result.returncode == 0:
            return float(result.stdout.strip())
    except Exception as e:
        print(f"Error getting video duration: {e}")
    return None

def create_video_thumbnail(video_path, thumbnail_path):
    """Create thumbnail from video using ffmpeg"""
    try:
        cmd = [
            'ffmpeg', '-i', video_path, '-ss', '00:00:01.000',
            '-vframes', '1', '-vf', 'scale=400:-1', thumbnail_path,
            '-y'  # Overwrite output file
        ]
        result = subprocess.run(cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        return result.returncode == 0
    except Exception as e:
        print(f"Error creating thumbnail: {e}")
    return False

def get_email_settings():
    """Get email settings from database"""
    try:
        return {
            'smtp_server': Settings.get('email_smtp_server', 'smtp.gmail.com'),
            'smtp_port': Settings.get('email_smtp_port', '587'),
            'smtp_username': Settings.get('email_smtp_username', ''),
            'smtp_password': Settings.get('email_smtp_password', ''),
            'imap_server': Settings.get('email_imap_server', 'imap.gmail.com'),
            'imap_port': Settings.get('email_imap_port', '993'),
            'imap_username': Settings.get('email_imap_username', ''),
            'imap_password': Settings.get('email_imap_password', ''),
            'monitor_email': Settings.get('email_monitor_email', ''),
            'enabled': Settings.get('email_enabled', 'false').lower() == 'true'
        }
    except Exception as e:
        print(f"Error getting email settings: {e}")
        # Return default settings if database is not ready
        return {
            'smtp_server': 'smtp.gmail.com',
            'smtp_port': '587',
            'smtp_username': '',
            'smtp_password': '',
            'imap_server': 'imap.gmail.com',
            'imap_port': '993',
            'imap_username': '',
            'imap_password': '',
            'monitor_email': '',
            'enabled': False
        }

def get_immich_settings():
    """Get Immich settings from database"""
    try:
        return {
            'enabled': Settings.get('immich_enabled', 'false').lower() == 'true',
            'server_url': Settings.get('immich_server_url', ''),
            'api_key': Settings.get('immich_api_key', ''),
            'user_id': Settings.get('immich_user_id', ''),
            'album_name': Settings.get('immich_album_name', 'Wedding Gallery'),
            'sync_photos': Settings.get('immich_sync_photos', 'true').lower() == 'true',
            'sync_videos': Settings.get('immich_sync_videos', 'true').lower() == 'true',
            'sync_guestbook': Settings.get('immich_sync_guestbook', 'true').lower() == 'true',
            'sync_messages': Settings.get('immich_sync_messages', 'true').lower() == 'true',
            'sync_photobooth': Settings.get('immich_sync_photobooth', 'true').lower() == 'true'
        }
    except Exception as e:
        print(f"Error getting Immich settings: {e}")
        return {
            'enabled': False,
            'server_url': '',
            'api_key': '',
            'user_id': '',
            'album_name': 'Wedding Gallery',
            'sync_photos': True,
            'sync_videos': True,
            'sync_guestbook': True,
            'sync_messages': True,
            'sync_photobooth': True
        }

def get_sso_settings():
    """Get SSO settings from database"""
    try:
        return {
            'enabled': Settings.get('sso_enabled', 'false').lower() == 'true',
            'provider': Settings.get('sso_provider', 'google'),  # google, azure, okta, custom
            'client_id': Settings.get('sso_client_id', ''),
            'client_secret': Settings.get('sso_client_secret', ''),
            'authorization_url': Settings.get('sso_authorization_url', ''),
            'token_url': Settings.get('sso_token_url', ''),
            'userinfo_url': Settings.get('sso_userinfo_url', ''),
            'redirect_uri': Settings.get('sso_redirect_uri', ''),
            'scope': Settings.get('sso_scope', 'openid email profile'),
            'allowed_domains': Settings.get('sso_allowed_domains', '').split(','),
            'allowed_emails': Settings.get('sso_allowed_emails', '').split(','),
            'admin_key_fallback': Settings.get('sso_admin_key_fallback', 'true').lower() == 'true'
        }
    except Exception as e:
        print(f"Error getting SSO settings: {e}")
        return {
            'enabled': False,
            'provider': 'google',
            'client_id': '',
            'client_secret': '',
            'authorization_url': '',
            'token_url': '',
            'userinfo_url': '',
            'redirect_uri': '',
            'scope': 'openid email profile',
            'allowed_domains': [],
            'allowed_emails': [],
            'admin_key_fallback': True
        }

def verify_admin_access(admin_key=None, user_email=None, user_domain=None):
    """Verify admin access using either key-based or SSO authentication"""
    # First check if SSO is enabled
    sso_settings = get_sso_settings()
    
    if sso_settings['enabled']:
        # SSO is enabled, check if user is authenticated via SSO
        if user_email:
            # Check allowed emails
            if sso_settings['allowed_emails'] and user_email in sso_settings['allowed_emails']:
                return True
            
            # Check allowed domains
            if user_domain and sso_settings['allowed_domains']:
                for domain in sso_settings['allowed_domains']:
                    if domain.strip() and user_domain.lower().endswith(domain.strip().lower()):
                        return True
        
        # If SSO fallback is enabled, also check admin key
        if sso_settings['admin_key_fallback'] and admin_key == 'wedding2024':
            return True
            
        return False
    else:
        # SSO is disabled, use key-based authentication
        return admin_key == 'wedding2024'

def send_confirmation_email(recipient_email, photo_count, gallery_url):
    """Send confirmation email to user who uploaded photos via email"""
    try:
        email_settings = get_email_settings()
        if not email_settings['enabled'] or not email_settings['smtp_username']:
            return False
            
        msg = MIMEMultipart()
        msg['From'] = email_settings['smtp_username']
        msg['To'] = recipient_email
        msg['Subject'] = "Thank you for sharing your wedding photos!"
        
        body = f"""
        Hi there!
        
        Thank you so much for sharing your wedding photos with us! We've successfully added {photo_count} photo(s) to our wedding gallery.
        
        You can view all the photos here: {gallery_url}
        
        We're so grateful to have these memories captured from your perspective. Thank you for being part of our special day!
        
        Best wishes,
        The Happy Couple
        """
        
        msg.attach(MIMEText(body, 'plain'))
        
        # Send email
        server = smtplib.SMTP(email_settings['smtp_server'], int(email_settings['smtp_port']))
        server.starttls()
        server.login(email_settings['smtp_username'], email_settings['smtp_password'])
        server.send_message(msg)
        server.quit()
        
        return True
    except Exception as e:
        print(f"Error sending confirmation email: {e}")
        return False

def send_rejection_email(recipient_email, reason):
    """Send rejection email to user who sent non-photo content"""
    try:
        email_settings = get_email_settings()
        if not email_settings['enabled'] or not email_settings['smtp_username']:
            return False
            
        msg = MIMEMultipart()
        msg['From'] = email_settings['smtp_username']
        msg['To'] = recipient_email
        msg['Subject'] = "Photo upload - only photos accepted"
        
        body = f"""
        Hi there!
        
        Thank you for trying to share content with our wedding gallery! However, we can only accept photo attachments at this time.
        
        {reason}
        
        Please send only photo files (JPG, PNG, GIF, WebP) as attachments to this email address.
        
        Thank you for understanding!
        
        Best wishes,
        The Happy Couple
        """
        
        msg.attach(MIMEText(body, 'plain'))
        
        # Send email
        server = smtplib.SMTP(email_settings['smtp_server'], int(email_settings['smtp_port']))
        server.starttls()
        server.login(email_settings['smtp_username'], email_settings['smtp_password'])
        server.send_message(msg)
        server.quit()
        
        return True
    except Exception as e:
        print(f"Error sending rejection email: {e}")
        return False

def sync_file_to_immich(file_path, filename, description=""):
    """Sync a file to Immich server"""
    try:
        immich_settings = get_immich_settings()
        if not immich_settings['enabled'] or not immich_settings['server_url'] or not immich_settings['api_key']:
            return False, "Immich sync not configured"
        
        # Check if file exists
        if not os.path.exists(file_path):
            return False, f"File not found: {file_path}"
        
        # Prepare headers for Immich API
        headers = {
            'x-api-key': immich_settings['api_key'],
            'Content-Type': 'application/octet-stream'
        }
        
        # Upload file to Immich
        upload_url = f"{immich_settings['server_url'].rstrip('/')}/api/asset/upload"
        
        with open(file_path, 'rb') as f:
            files = {'assetData': (filename, f, 'application/octet-stream')}
            data = {
                'deviceAssetId': filename,
                'deviceId': 'wedding-gallery',
                'fileCreatedAt': datetime.now().isoformat(),
                'fileModifiedAt': datetime.now().isoformat(),
                'isFavorite': False,
                'fileExtension': Path(filename).suffix.lower().lstrip('.'),
                'description': description
            }
            
            response = requests.post(upload_url, headers=headers, files=files, data=data, timeout=30)
            
            if response.status_code == 201:
                asset_data = response.json()
                asset_id = asset_data.get('id')
                
                # Add to album if specified
                if immich_settings['album_name']:
                    album_url = f"{immich_settings['server_url'].rstrip('/')}/api/album/{immich_settings['album_name']}/assets"
                    album_data = {'ids': [asset_id]}
                    album_response = requests.put(album_url, headers=headers, json=album_data, timeout=10)
                
                return True, asset_id
            else:
                return False, f"Immich API error: {response.status_code} - {response.text}"
                
    except Exception as e:
        return False, f"Error syncing to Immich: {str(e)}"

def sync_all_to_immich():
    """Sync all eligible files to Immich"""
    try:
        immich_settings = get_immich_settings()
        if not immich_settings['enabled']:
            return False, "Immich sync not enabled"
        
        synced_count = 0
        error_count = 0
        
        # Sync photos
        if immich_settings['sync_photos']:
            photos = Photo.query.filter_by(media_type='image').all()
            for photo in photos:
                file_path = os.path.join(app.config['UPLOAD_FOLDER'], photo.filename)
                description = f"Wedding photo by {photo.uploader_name}"
                if photo.description:
                    description += f" - {photo.description}"
                
                success, result = sync_file_to_immich(file_path, photo.filename, description)
                
                # Log sync attempt
                sync_log = ImmichSyncLog(
                    filename=photo.filename,
                    file_path=file_path,
                    status='success' if success else 'error',
                    immich_asset_id=result if success else None,
                    error_message=str(result) if not success else None
                )
                db.session.add(sync_log)
                
                if success:
                    synced_count += 1
                else:
                    error_count += 1
        
        # Sync videos
        if immich_settings['sync_videos']:
            videos = Photo.query.filter_by(media_type='video').all()
            for video in videos:
                file_path = os.path.join(app.config['VIDEO_FOLDER'], video.filename)
                description = f"Wedding video by {video.uploader_name}"
                if video.description:
                    description += f" - {video.description}"
                
                success, result = sync_file_to_immich(file_path, video.filename, description)
                
                sync_log = ImmichSyncLog(
                    filename=video.filename,
                    file_path=file_path,
                    status='success' if success else 'error',
                    immich_asset_id=result if success else None,
                    error_message=str(result) if not success else None
                )
                db.session.add(sync_log)
                
                if success:
                    synced_count += 1
                else:
                    error_count += 1
        
        # Sync guestbook photos
        if immich_settings['sync_guestbook']:
            guestbook_entries = GuestbookEntry.query.filter(GuestbookEntry.photo_filename.isnot(None)).all()
            for entry in guestbook_entries:
                file_path = os.path.join(app.config['GUESTBOOK_UPLOAD_FOLDER'], entry.photo_filename)
                description = f"Guestbook photo by {entry.name} from {entry.location}"
                if entry.message:
                    description += f" - {entry.message[:100]}"
                
                success, result = sync_file_to_immich(file_path, entry.photo_filename, description)
                
                sync_log = ImmichSyncLog(
                    filename=entry.photo_filename,
                    file_path=file_path,
                    status='success' if success else 'error',
                    immich_asset_id=result if success else None,
                    error_message=str(result) if not success else None
                )
                db.session.add(sync_log)
                
                if success:
                    synced_count += 1
                else:
                    error_count += 1
        
        # Sync message photos
        if immich_settings['sync_messages']:
            messages = Message.query.filter(Message.photo_filename.isnot(None)).all()
            for message in messages:
                file_path = os.path.join(app.config['MESSAGE_UPLOAD_FOLDER'], message.photo_filename)
                description = f"Message photo by {message.author_name}"
                if message.content:
                    description += f" - {message.content[:100]}"
                
                success, result = sync_file_to_immich(file_path, message.photo_filename, description)
                
                sync_log = ImmichSyncLog(
                    filename=message.photo_filename,
                    file_path=file_path,
                    status='success' if success else 'error',
                    immich_asset_id=result if success else None,
                    error_message=str(result) if not success else None
                )
                db.session.add(sync_log)
                
                if success:
                    synced_count += 1
                else:
                    error_count += 1
        
        # Sync photobooth photos
        if immich_settings['sync_photobooth']:
            photobooth_photos = Photo.query.filter_by(is_photobooth=True).all()
            for photo in photobooth_photos:
                file_path = os.path.join(app.config['PHOTOBOOTH_FOLDER'], photo.filename)
                description = f"Photobooth photo by {photo.uploader_name}"
                if photo.description:
                    description += f" - {photo.description}"
                
                success, result = sync_file_to_immich(file_path, photo.filename, description)
                
                sync_log = ImmichSyncLog(
                    filename=photo.filename,
                    file_path=file_path,
                    status='success' if success else 'error',
                    immich_asset_id=result if success else None,
                    error_message=str(result) if not success else None
                )
                db.session.add(sync_log)
                
                if success:
                    synced_count += 1
                else:
                    error_count += 1
        
        db.session.commit()
        return True, f"Synced {synced_count} files, {error_count} errors"
        
    except Exception as e:
        return False, f"Error during sync: {str(e)}"

def process_email_photos():
    """Process incoming emails and extract photos"""
    try:
        email_settings = get_email_settings()
        if not email_settings['enabled'] or not email_settings['imap_username']:
            print("Email processing skipped - not enabled or IMAP username not configured")
            return
            
        # Connect to IMAP server
        print(f"Connecting to IMAP server: {email_settings['imap_server']}:{email_settings['imap_port']}")
        mail = imaplib.IMAP4_SSL(email_settings['imap_server'], int(email_settings['imap_port']))
        mail.login(email_settings['imap_username'], email_settings['imap_password'])
        mail.select('INBOX')
        
        # Search for unread emails
        status, messages = mail.search(None, 'UNSEEN')
        
        if status != 'OK':
            print(f"IMAP search failed with status: {status}")
            return
            
        if not messages[0]:
            print("No unread emails found")
            return
            
        print(f"Found {len(messages[0].split())} unread email(s)")
            
        for num in messages[0].split():
            try:
                status, msg_data = mail.fetch(num, '(RFC822)')
                if status != 'OK':
                    continue
                    
                email_body = msg_data[0][1]
                email_message = email.message_from_bytes(email_body)
                
                sender_email = email_message['from']
                subject = email_message.get('subject', '')
                # Extract email from "Name <email@domain.com>" format
                if '<' in sender_email and '>' in sender_email:
                    sender_email = sender_email.split('<')[1].split('>')[0]
                
                photo_count = 0
                has_photos = False
                has_non_photos = False
                error_message = None
                
                # Process attachments
                for part in email_message.walk():
                    if part.get_content_maintype() == 'multipart':
                        continue
                    if part.get('Content-Disposition') is None:
                        continue
                        
                    filename = part.get_filename()
                    if filename:
                        # Check if it's a photo
                        if is_image(filename):
                            has_photos = True
                            # Save the photo
                            file_data = part.get_payload(decode=True)
                            if file_data:
                                # Generate unique filename
                                timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
                                safe_filename = secure_filename(filename)
                                unique_filename = f"{timestamp}_{safe_filename}"
                                file_path = os.path.join(app.config['UPLOAD_FOLDER'], unique_filename)
                                
                                with open(file_path, 'wb') as f:
                                    f.write(file_data)
                                
                                # Create database entry
                                photo = Photo(
                                    filename=unique_filename,
                                    original_filename=filename,
                                    uploader_name=sender_email,
                                    upload_date=datetime.utcnow()
                                )
                                db.session.add(photo)
                                photo_count += 1
                        else:
                            has_non_photos = True
                
                # Determine status and create log entry
                if photo_count > 0:
                    status = 'success'
                    response_type = 'confirmation'
                    response_sent = True
                    
                    # Commit database changes
                    db.session.commit()
                    
                    # Send confirmation email
                    public_url = Settings.get('public_url', '')
                    if public_url:
                        send_confirmation_email(sender_email, photo_count, public_url)
                
                elif has_non_photos and not has_photos:
                    status = 'rejected'
                    response_type = 'rejection'
                    response_sent = True
                    send_rejection_email(sender_email, "We received your email but it didn't contain any photo attachments.")
                
                else:
                    status = 'rejected'
                    response_type = 'rejection'
                    response_sent = True
                    send_rejection_email(sender_email, "We received your email but it didn't contain any photo attachments.")
                
                # Create email log entry
                email_log = EmailLog(
                    sender_email=sender_email,
                    subject=subject,
                    processed_at=datetime.utcnow(),
                    status=status,
                    photo_count=photo_count,
                    response_sent=response_sent,
                    response_type=response_type
                )
                db.session.add(email_log)
                db.session.commit()
                
                # Mark email as read
                mail.store(num, '+FLAGS', '\\Seen')
                
            except Exception as e:
                print(f"Error processing email: {e}")
                # Log the error
                try:
                    email_log = EmailLog(
                        sender_email=sender_email if 'sender_email' in locals() else 'Unknown',
                        subject=subject if 'subject' in locals() else '',
                        processed_at=datetime.utcnow(),
                        status='error',
                        error_message=str(e),
                        response_sent=False
                    )
                    db.session.add(email_log)
                    db.session.commit()
                except Exception as log_error:
                    print(f"Error logging email error: {log_error}")
                continue
        
        mail.close()
        mail.logout()
        print("Email processing completed")
        
    except Exception as e:
        print(f"Error in email processing: {e}")
        # Ensure we don't leave any uncommitted database changes
        try:
            db.session.rollback()
        except Exception as rollback_error:
            print(f"Error during rollback: {rollback_error}")

def start_email_monitor():
    """Start the email monitoring thread"""
    def monitor_emails():
        with app.app_context():
            print("Email monitoring thread started")
            while True:
                try:
                    process_email_photos()
                    time.sleep(300)  # Check every 5 minutes
                except Exception as e:
                    print(f"Email monitor error: {e}")
                    time.sleep(600)  # Wait 10 minutes on error
    
    thread = threading.Thread(target=monitor_emails, daemon=True)
    thread.start()
    print("Email monitoring thread created")

@app.route('/')
def index():
    # Get or create user identifier for all visitors
    user_identifier = request.cookies.get('user_identifier', '')
    if not user_identifier:
        user_identifier = secrets.token_hex(16)
    
    # Get user name from cookie
    user_name = request.cookies.get('user_name', '')
    has_seen_welcome = request.cookies.get('has_seen_welcome', '')
    
    # Get welcome modal settings
    welcome_settings = Settings.get('welcome_modal', '{}')
    welcome_settings = json.loads(welcome_settings) if welcome_settings else {}
    
    # Default values if not set
    if not welcome_settings:
        welcome_settings = {
            'enabled': True,
            'title': 'Welcome to Our Wedding Gallery!',
            'message': 'Thank you so much for celebrating with us! We\'d love to see the wedding through your eyes. Feel free to upload your photos and browse the gallery.',
            'instructions': [
                'Click "Upload Photo/Video" to share your pictures or short videos',
                'Browse the gallery to see all photos and videos',
                'Click on any photo or video to like or comment',
                'No login required - just add your name when uploading or commenting'
            ],
            'couple_photo': '',
            'show_once': True
        }
    
    show_modal = welcome_settings.get('enabled', True) and (not has_seen_welcome or not welcome_settings.get('show_once', True))
    
    # Get search parameters
    search_query = request.args.get('search', '').strip()
    media_filter = request.args.get('media_type', '')
    tag_filter = request.args.get('tag', '')
    
    # Get all content with pagination (photos, videos, photobooth, and emailed content)
    page = request.args.get('page', 1, type=int)
    per_page = 20  # Increased for better performance
    
    # Build query with filters using optimized approach
    photos_query = Photo.query.options(
        db.joinedload(Photo.comments)
    )
    
    # Apply search filter with optimized LIKE queries
    if search_query:
        search_term = f'%{search_query}%'
        photos_query = photos_query.filter(
            db.or_(
                Photo.uploader_name.ilike(search_term),
                Photo.description.ilike(search_term),
                Photo.tags.ilike(search_term)
            )
        )
    
    # Apply media type filter
    if media_filter:
        if media_filter == 'photos':
            photos_query = photos_query.filter(Photo.media_type == 'image')
        elif media_filter == 'videos':
            photos_query = photos_query.filter(Photo.media_type == 'video')
        elif media_filter == 'photobooth':
            photos_query = photos_query.filter(Photo.is_photobooth == True)
    
    # Apply tag filter
    if tag_filter:
        photos_query = photos_query.filter(Photo.tags.ilike(f'%{tag_filter}%'))
    
    # Order by upload date (newest first) - this uses the optimized index
    photos_query = photos_query.order_by(Photo.upload_date.desc())
    photos = photos_query.paginate(page=page, per_page=per_page, error_out=False)
    
    # Get all unique tags for filter dropdown with caching
    @db_optimizer.cache_query('all_tags', lambda: None, 1800)  # Cache for 30 minutes
    def get_all_tags():
        all_tags = set()
        # Use a more efficient query to get tags
        tag_photos = Photo.query.filter(Photo.tags.isnot(None)).with_entities(Photo.tags).all()
        for photo in tag_photos:
            if photo.tags:
                tags = [tag.strip() for tag in photo.tags.split(',') if tag.strip()]
                all_tags.update(tags)
        return sorted(list(all_tags))
    
    all_tags = get_all_tags()
    
    # Get email settings for the welcome modal
    email_settings = get_email_settings()
    
    # Create response with user identifier cookie if needed
    if not request.cookies.get('user_identifier'):
        resp = make_response(render_template('index.html', 
                                          photos=photos, 
                                          user_name=user_name,
                                          welcome_settings=welcome_settings,
                                          show_modal=show_modal,
                                          email_settings=email_settings,
                                          search_query=search_query,
                                          media_filter=media_filter,
                                          tag_filter=tag_filter,
                                          all_tags=all_tags))
        resp.set_cookie('user_identifier', user_identifier, max_age=365*24*60*60)  # 1 year
        return resp
    
    return render_template('index.html', 
                         photos=photos, 
                         user_name=user_name,
                         welcome_settings=welcome_settings,
                         show_modal=show_modal,
                         email_settings=email_settings,
                         search_query=search_query,
                         media_filter=media_filter,
                         tag_filter=tag_filter,
                         all_tags=all_tags)

@app.route('/upload', methods=['GET', 'POST'])
def upload():
    if request.method == 'POST':
        if 'photo' not in request.files:
            return redirect(request.url)
        
        file = request.files['photo']
        if file.filename == '':
            return redirect(request.url)
        
        if file and allowed_file(file.filename):
            filename = secure_filename(file.filename)
            timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
            
            uploader_name = request.form.get('uploader_name', 'Anonymous').strip() or 'Anonymous'
            description = request.form.get('description', '')
            tags = request.form.get('tags', '').strip()
            
            # Get or create user identifier
            user_identifier = request.cookies.get('user_identifier', '')
            if not user_identifier:
                user_identifier = secrets.token_hex(16)
            
            if is_video(filename):
                # Handle video upload
                filename = f"{timestamp}_{filename}"
                filepath = os.path.join(app.config['VIDEO_FOLDER'], filename)
                file.save(filepath)
                
                # Check video duration
                duration = get_video_duration(filepath)
                if duration and duration > app.config['MAX_VIDEO_DURATION']:
                    os.remove(filepath)
                    return render_template('upload.html', 
                                         user_name=request.cookies.get('user_name', ''),
                                         error=f'Video must be {app.config["MAX_VIDEO_DURATION"]} seconds or less')
                
                # Create thumbnail
                thumbnail_filename = f"thumb_{timestamp}_{os.path.splitext(filename)[0]}.jpg"
                thumbnail_path = os.path.join(app.config['THUMBNAIL_FOLDER'], thumbnail_filename)
                
                if not create_video_thumbnail(filepath, thumbnail_path):
                    thumbnail_filename = None
                
                photo = Photo(
                    filename=filename,
                    original_filename=file.filename,
                    uploader_name=uploader_name,
                    uploader_identifier=user_identifier,
                    description=description,
                    tags=tags,
                    media_type='video',
                    thumbnail_filename=thumbnail_filename,
                    duration=duration
                )
            else:
                # Handle image upload
                filename = f"{timestamp}_{filename}"
                filepath = os.path.join(app.config['UPLOAD_FOLDER'], filename)
                file.save(filepath)
                
                photo = Photo(
                    filename=filename,
                    original_filename=file.filename,
                    uploader_name=uploader_name,
                    uploader_identifier=user_identifier,
                    description=description,
                    tags=tags,
                    media_type='image'
                )
            
            db.session.add(photo)
            db.session.commit()
            
            # Sync to Immich if enabled
            try:
                immich_settings = get_immich_settings()
                if immich_settings['enabled']:
                    if photo.media_type == 'video' and immich_settings['sync_videos']:
                        file_path = os.path.join(app.config['VIDEO_FOLDER'], photo.filename)
                        description = f"Wedding video by {photo.uploader_name}"
                        if photo.description:
                            description += f" - {photo.description}"
                        sync_file_to_immich(file_path, photo.filename, description)
                    elif photo.media_type == 'image' and immich_settings['sync_photos']:
                        file_path = os.path.join(app.config['UPLOAD_FOLDER'], photo.filename)
                        description = f"Wedding photo by {photo.uploader_name}"
                        if photo.description:
                            description += f" - {photo.description}"
                        sync_file_to_immich(file_path, photo.filename, description)
            except Exception as e:
                print(f"Error syncing to Immich: {e}")
            
            # Save user name in cookie
            resp = make_response(redirect(url_for('index')))
            resp.set_cookie('user_name', uploader_name, max_age=30*24*60*60)  # 30 days
            resp.set_cookie('user_identifier', user_identifier, max_age=365*24*60*60)  # 1 year
            return resp
    
    # Get or create user identifier for visitors to upload page
    user_identifier = request.cookies.get('user_identifier', '')
    if not user_identifier:
        user_identifier = secrets.token_hex(16)
    
    user_name = request.cookies.get('user_name', '')
    email_settings = get_email_settings()
    
    # Create response with user identifier cookie if needed
    if not request.cookies.get('user_identifier'):
        resp = make_response(render_template('upload.html', user_name=user_name, email_settings=email_settings))
        resp.set_cookie('user_identifier', user_identifier, max_age=365*24*60*60)  # 1 year
        return resp
    
    return render_template('upload.html', user_name=user_name, email_settings=email_settings)

@app.route('/photobooth')
def photobooth():
    user_name = request.cookies.get('user_name', '')
    
    # Get the current border settings
    border_settings = Settings.get('photobooth_border', '{}')
    border_settings = json.loads(border_settings) if border_settings else {}
    
    return render_template('photobooth.html', 
                         user_name=user_name,
                         border_url=border_settings.get('border_url', ''))

@app.route('/api/photobooth/save', methods=['POST'])
def save_photobooth_photo():
    data = request.get_json()
    
    if not data or 'image' not in data:
        return jsonify({'error': 'No image data provided'}), 400
    
    try:
        # Extract base64 image data
        image_data = data['image'].split(',')[1]
        image_bytes = base64.b64decode(image_data)
        
        # Generate filename
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        filename = f"photobooth_{timestamp}.png"
        filepath = os.path.join(app.config['PHOTOBOOTH_FOLDER'], filename)
        
        # Save image
        with open(filepath, 'wb') as f:
            f.write(image_bytes)
        
        # Create database entry if uploading to gallery
        if data.get('upload_to_gallery', False):
            uploader_name = data.get('uploader_name', 'Anonymous').strip() or 'Anonymous'
            description = data.get('description', 'Photo from Virtual Photobooth')
            tags = data.get('tags', '').strip()
            
            # Get or create user identifier
            user_identifier = request.cookies.get('user_identifier', '')
            if not user_identifier:
                user_identifier = secrets.token_hex(16)
            
            photo = Photo(
                filename=filename,
                original_filename=filename,
                uploader_name=uploader_name,
                uploader_identifier=user_identifier,
                description=description,
                tags=tags,
                media_type='image',
                is_photobooth=True
            )
            
            db.session.add(photo)
            db.session.commit()
            
            # Sync to Immich if enabled
            try:
                immich_settings = get_immich_settings()
                if immich_settings['enabled'] and immich_settings['sync_photobooth']:
                    file_path = os.path.join(app.config['PHOTOBOOTH_FOLDER'], photo.filename)
                    description = f"Photobooth photo by {photo.uploader_name}"
                    if photo.description:
                        description += f" - {photo.description}"
                    sync_file_to_immich(file_path, photo.filename, description)
            except Exception as e:
                print(f"Error syncing photobooth to Immich: {e}")
            
            # Save user name and identifier in cookies
            resp = jsonify({
                'success': True,
                'filename': filename,
                'uploaded': True,
                'photo_id': photo.id
            })
            resp.set_cookie('user_name', uploader_name, max_age=30*24*60*60)  # 30 days
            resp.set_cookie('user_identifier', user_identifier, max_age=365*24*60*60)  # 1 year
            return resp
        
        return jsonify({
            'success': True,
            'filename': filename,
            'uploaded': False
        })
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/photo/<int:photo_id>')
def view_photo(photo_id):
    photo = Photo.query.get_or_404(photo_id)
    user_name = request.cookies.get('user_name', '')
    user_identifier = request.cookies.get('user_identifier', '')
    
    # Check if user has liked this photo
    has_liked = False
    if user_identifier:
        has_liked = Like.query.filter_by(photo_id=photo_id, user_identifier=user_identifier).first() is not None
    
    return render_template('photo_detail.html', photo=photo, user_name=user_name, has_liked=has_liked)

@app.route('/guestbook')
def guestbook():
    user_name = request.cookies.get('user_name', '')
    entries = GuestbookEntry.query.order_by(GuestbookEntry.created_at.desc()).all()
    return render_template('guestbook.html', user_name=user_name, entries=entries)

@app.route('/guestbook/sign', methods=['GET', 'POST'])
def sign_guestbook():
    if request.method == 'POST':
        name = request.form.get('name', '').strip()
        message = request.form.get('message', '').strip()
        location = request.form.get('location', '').strip()
        
        if name and message:
            # Handle optional photo upload
            photo_filename = None
            if 'photo' in request.files:
                file = request.files['photo']
                if file and file.filename != '' and allowed_file(file.filename):
                    filename = secure_filename(file.filename)
                    timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
                    filename = f"guestbook_{timestamp}_{filename}"
                    filepath = os.path.join(app.config['GUESTBOOK_UPLOAD_FOLDER'], filename)
                    file.save(filepath)
                    photo_filename = filename
            
            entry = GuestbookEntry(
                name=name,
                message=message,
                location=location,
                photo_filename=photo_filename
            )
            db.session.add(entry)
            db.session.commit()
            
            # Sync guestbook photo to Immich if enabled
            if photo_filename:
                try:
                    immich_settings = get_immich_settings()
                    if immich_settings['enabled'] and immich_settings['sync_guestbook']:
                        file_path = os.path.join(app.config['GUESTBOOK_UPLOAD_FOLDER'], photo_filename)
                        description = f"Guestbook photo by {entry.name} from {entry.location}"
                        if entry.message:
                            description += f" - {entry.message[:100]}"
                        sync_file_to_immich(file_path, photo_filename, description)
                except Exception as e:
                    print(f"Error syncing guestbook photo to Immich: {e}")
            
            # Save user name in cookie
            resp = make_response(redirect(url_for('guestbook')))
            resp.set_cookie('user_name', name, max_age=30*24*60*60)  # 30 days
            return resp
        else:
            return render_template('sign_guestbook.html', 
                                 user_name=request.cookies.get('user_name', ''),
                                 error='Name and message are required')
    
    user_name = request.cookies.get('user_name', '')
    return render_template('sign_guestbook.html', user_name=user_name)

# Message Board Routes
@app.route('/messages')
def message_board():
    user_name = request.cookies.get('user_name', '')
    user_identifier = request.cookies.get('user_identifier', '')
    
    # Get all visible messages
    messages = Message.query.filter_by(is_hidden=False).order_by(Message.created_at.desc()).all()
    
    # Check which messages the user has liked
    liked_messages = set()
    if user_identifier:
        likes = MessageLike.query.filter_by(user_identifier=user_identifier).all()
        liked_messages = {like.message_id for like in likes}
    
    return render_template('message_board.html', 
                         user_name=user_name, 
                         messages=messages,
                         liked_messages=liked_messages)

@app.route('/messages/new', methods=['GET', 'POST'])
def new_message():
    if request.method == 'POST':
        author_name = request.form.get('author_name', '').strip() or 'Anonymous'
        content = request.form.get('content', '').strip()
        
        if content:
            # Get or create user identifier
            user_identifier = request.cookies.get('user_identifier', '')
            if not user_identifier:
                user_identifier = secrets.token_hex(16)
            
            # Handle optional photo upload
            photo_filename = None
            if 'photo' in request.files:
                file = request.files['photo']
                if file and file.filename != '' and allowed_file(file.filename):
                    filename = secure_filename(file.filename)
                    timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
                    filename = f"message_{timestamp}_{filename}"
                    filepath = os.path.join(app.config['MESSAGE_UPLOAD_FOLDER'], filename)
                    file.save(filepath)
                    photo_filename = filename
            
            message = Message(
                author_name=author_name,
                author_identifier=user_identifier,
                content=content,
                photo_filename=photo_filename
            )
            db.session.add(message)
            db.session.commit()
            
            # Sync message photo to Immich if enabled
            if photo_filename:
                try:
                    immich_settings = get_immich_settings()
                    if immich_settings['enabled'] and immich_settings['sync_messages']:
                        file_path = os.path.join(app.config['MESSAGE_UPLOAD_FOLDER'], photo_filename)
                        description = f"Message photo by {message.author_name}"
                        if message.content:
                            description += f" - {message.content[:100]}"
                        sync_file_to_immich(file_path, photo_filename, description)
                except Exception as e:
                    print(f"Error syncing message photo to Immich: {e}")
            
            # Save user name in cookie
            resp = make_response(redirect(url_for('message_board')))
            resp.set_cookie('user_name', author_name, max_age=30*24*60*60)  # 30 days
            resp.set_cookie('user_identifier', user_identifier, max_age=365*24*60*60)  # 1 year
            return resp
        else:
            return render_template('new_message.html', 
                                 user_name=request.cookies.get('user_name', ''),
                                 error='Message content is required')
    
    user_name = request.cookies.get('user_name', '')
    return render_template('new_message.html', user_name=user_name)

@app.route('/api/message/<int:message_id>/like', methods=['POST'])
def toggle_message_like(message_id):
    message = Message.query.get_or_404(message_id)
    user_identifier = request.cookies.get('user_identifier', '')
    
    if not user_identifier:
        user_identifier = secrets.token_hex(16)
    
    existing_like = MessageLike.query.filter_by(message_id=message_id, user_identifier=user_identifier).first()
    
    if existing_like:
        db.session.delete(existing_like)
        message.likes = max(0, message.likes - 1)
        liked = False
    else:
        new_like = MessageLike(message_id=message_id, user_identifier=user_identifier)
        db.session.add(new_like)
        message.likes += 1
        liked = True
    
    db.session.commit()
    
    # Create database notification for the message author if someone else liked it
    if liked and message.author_identifier and message.author_identifier != user_identifier:
        liker_name = request.cookies.get('user_name', 'Anonymous')
        
        # Create notification with push notification
        create_notification_with_push(
            user_identifier=message.author_identifier,
            title='❤️ New Like!',
            message=f'{liker_name} just liked your message!',
            notification_type='like',
            content_type='message',
            content_id=message_id
        )
    
    # Prepare notification data for the message author
    notification_data = {
        'type': 'message_like',
        'action': 'liked' if liked else 'unliked',
        'message_id': message_id,
        'message_author': message.author_name,
        'author_identifier': message.author_identifier,
        'liker_identifier': user_identifier,
        'liker_name': request.cookies.get('user_name', 'Anonymous'),
        'total_likes': message.likes
    }
    
    resp = jsonify({
        'likes': message.likes, 
        'liked': liked,
        'notification_data': notification_data
    })
    resp.set_cookie('user_identifier', user_identifier, max_age=365*24*60*60)  # 1 year
    return resp

@app.route('/api/message/<int:message_id>/comment', methods=['POST'])
def add_message_comment(message_id):
    message = Message.query.get_or_404(message_id)
    data = request.get_json()
    
    commenter_name = data.get('commenter_name', 'Anonymous').strip() or 'Anonymous'
    content = data.get('content', '').strip()
    
    if not content:
        return jsonify({'error': 'Comment cannot be empty'}), 400
    
    comment = MessageComment(
        message_id=message_id,
        commenter_name=commenter_name,
        content=content
    )
    db.session.add(comment)
    db.session.commit()
    
    # Create database notification for the message author if someone else commented
    user_identifier = request.cookies.get('user_identifier', '')
    if message.author_identifier and message.author_identifier != user_identifier:
        # Create notification with push notification
        create_notification_with_push(
            user_identifier=message.author_identifier,
            title='💬 New Comment!',
            message=f'{commenter_name} commented on your message!',
            notification_type='comment',
            content_type='message',
            content_id=message_id
        )
    
    # Prepare notification data for the message author
    notification_data = {
        'type': 'message_comment',
        'message_id': message_id,
        'message_author': message.author_name,
        'author_identifier': message.author_identifier,
        'commenter_name': commenter_name,
        'comment_content': content,
        'comment_id': comment.id
    }
    
    resp = jsonify({
        'id': comment.id,
        'commenter_name': comment.commenter_name,
        'content': comment.content,
        'created_at': comment.created_at.strftime('%B %d, %Y at %I:%M %p'),
        'notification_data': notification_data
    })
    resp.set_cookie('user_name', commenter_name, max_age=30*24*60*60)  # 30 days
    return resp

@app.route('/api/like/<int:photo_id>', methods=['POST'])
def toggle_like(photo_id):
    photo = Photo.query.get_or_404(photo_id)
    user_identifier = request.cookies.get('user_identifier', '')
    
    if not user_identifier:
        user_identifier = secrets.token_hex(16)
    
    existing_like = Like.query.filter_by(photo_id=photo_id, user_identifier=user_identifier).first()
    
    if existing_like:
        db.session.delete(existing_like)
        photo.likes = max(0, photo.likes - 1)
        liked = False
    else:
        new_like = Like(photo_id=photo_id, user_identifier=user_identifier)
        db.session.add(new_like)
        photo.likes += 1
        liked = True
    
    db.session.commit()
    
    # Check if photo should be added as a candidate for Photo of the Day
    if liked and photo.likes >= 3:
        # Check if already a candidate
        existing_candidate = PhotoOfDayCandidate.query.filter_by(photo_id=photo_id).first()
        if not existing_candidate:
            # Add as candidate
            candidate = PhotoOfDayCandidate(
                photo_id=photo_id,
                date_added=date.today(),
                is_selected=False
            )
            db.session.add(candidate)
            db.session.commit()
    
    # Create database notification for the photo uploader if someone else liked it
    if liked and photo.uploader_identifier and photo.uploader_identifier != user_identifier:
        liker_name = request.cookies.get('user_name', 'Anonymous')
        
        print(f"DEBUG: Creating like notification for photo {photo_id}")
        print(f"DEBUG: Photo uploader: {photo.uploader_identifier}")
        print(f"DEBUG: Liker: {user_identifier}")
        print(f"DEBUG: Liker name: {liker_name}")
        
        # Create notification with push notification
        notification = create_notification_with_push(
            user_identifier=photo.uploader_identifier,
            title='❤️ New Like!',
            message=f'{liker_name} just liked your photo!',
            notification_type='like',
            content_type='photo',
            content_id=photo_id
        )
        
        if notification:
            print(f"DEBUG: Like notification created successfully for {photo.uploader_identifier}")
        else:
            print(f"DEBUG: Failed to create like notification for {photo.uploader_identifier}")
    else:
        print(f"DEBUG: No like notification needed - liked: {liked}, uploader: {photo.uploader_identifier}, user: {user_identifier}")
    
    # Prepare notification data for the photo uploader
    notification_data = {
        'type': 'like',
        'action': 'liked' if liked else 'unliked',
        'photo_id': photo_id,
        'photo_uploader': photo.uploader_name,
        'uploader_identifier': photo.uploader_identifier,
        'liker_identifier': user_identifier,
        'liker_name': request.cookies.get('user_name', 'Anonymous'),
        'total_likes': photo.likes
    }
    
    resp = jsonify({
        'likes': photo.likes, 
        'liked': liked,
        'notification_data': notification_data
    })
    resp.set_cookie('user_identifier', user_identifier, max_age=365*24*60*60)  # 1 year
    return resp

@app.route('/api/comment/<int:photo_id>', methods=['POST'])
def add_comment(photo_id):
    photo = Photo.query.get_or_404(photo_id)
    data = request.get_json()
    
    commenter_name = data.get('commenter_name', 'Anonymous').strip() or 'Anonymous'
    content = data.get('content', '').strip()
    
    if not content:
        return jsonify({'error': 'Comment cannot be empty'}), 400
    
    comment = Comment(
        photo_id=photo_id,
        commenter_name=commenter_name,
        content=content
    )
    db.session.add(comment)
    db.session.commit()
    
    # Create database notification for the photo uploader if someone else commented
    user_identifier = request.cookies.get('user_identifier', '')
    if photo.uploader_identifier and photo.uploader_identifier != user_identifier:
        print(f"DEBUG: Creating comment notification for photo {photo_id}")
        print(f"DEBUG: Photo uploader: {photo.uploader_identifier}")
        print(f"DEBUG: Commenter: {user_identifier}")
        print(f"DEBUG: Commenter name: {commenter_name}")
        
        # Create notification with push notification
        notification = create_notification_with_push(
            user_identifier=photo.uploader_identifier,
            title='💬 New Comment!',
            message=f'{commenter_name} commented on your photo!',
            notification_type='comment',
            content_type='photo',
            content_id=photo_id
        )
        
        if notification:
            print(f"DEBUG: Comment notification created successfully for {photo.uploader_identifier}")
        else:
            print(f"DEBUG: Failed to create comment notification for {photo.uploader_identifier}")
    else:
        print(f"DEBUG: No comment notification needed - uploader: {photo.uploader_identifier}, commenter: {user_identifier}")
    
    # Prepare notification data for the photo uploader
    notification_data = {
        'type': 'comment',
        'photo_id': photo_id,
        'photo_uploader': photo.uploader_name,
        'uploader_identifier': photo.uploader_identifier,
        'commenter_name': commenter_name,
        'comment_content': content,
        'comment_id': comment.id
    }
    
    resp = jsonify({
        'id': comment.id,
        'commenter_name': comment.commenter_name,
        'content': comment.content,
        'created_at': comment.created_at.strftime('%B %d, %Y at %I:%M %p'),
        'notification_data': notification_data
    })
    resp.set_cookie('user_name', commenter_name, max_age=30*24*60*60)  # 30 days
    return resp

@app.route('/api/mark-welcome-seen', methods=['POST'])
def mark_welcome_seen():
    resp = jsonify({'success': True})
    resp.set_cookie('has_seen_welcome', 'true', max_age=365*24*60*60)  # 1 year
    return resp

@app.route('/admin')
def admin():
    # Check for SSO session first
    sso_user_email = session.get('sso_user_email')
    sso_user_domain = session.get('sso_user_domain')
    admin_key = request.args.get('key', '')
    
    # Verify admin access
    if not verify_admin_access(admin_key, sso_user_email, sso_user_domain):
        # If SSO is enabled, redirect to SSO login
        sso_settings = get_sso_settings()
        if sso_settings['enabled']:
            return redirect(url_for('sso_login'))
        else:
            return "Unauthorized", 401
    
    photos = Photo.query.order_by(Photo.upload_date.desc()).all()
    total_likes = sum(photo.likes for photo in photos)
    total_comments = Comment.query.count()
    guestbook_entries = GuestbookEntry.query.order_by(GuestbookEntry.created_at.desc()).all()
    
    # Get messages for admin
    all_messages = Message.query.order_by(Message.created_at.desc()).all()
    visible_messages = [m for m in all_messages if not m.is_hidden]
    hidden_messages = [m for m in all_messages if m.is_hidden]
    total_message_comments = MessageComment.query.count()
    
    # Get saved settings
    public_url = Settings.get('public_url', '')
    qr_settings = Settings.get('qr_settings', '{}')
    qr_settings = json.loads(qr_settings) if qr_settings else {}
    
    welcome_settings = Settings.get('welcome_modal', '{}')
    welcome_settings = json.loads(welcome_settings) if welcome_settings else {}
    
    border_settings = Settings.get('photobooth_border', '{}')
    border_settings = json.loads(border_settings) if border_settings else {}
    
    # Get timezone settings
    timezone_settings = Settings.get('timezone_settings', '{}')
    timezone_settings = json.loads(timezone_settings) if timezone_settings else {}
    
    # Calculate current time in selected timezone
    from app.utils.settings_utils import format_datetime_in_timezone, get_sso_settings, get_immich_settings
    from datetime import datetime
    current_time = format_datetime_in_timezone(datetime.utcnow())
    
    # Get email settings
    email_settings = {
        'enabled': Settings.get('email_enabled', 'false').lower() == 'true',
        'smtp_server': Settings.get('email_smtp_server', 'smtp.gmail.com'),
        'smtp_port': Settings.get('email_smtp_port', '587'),
        'smtp_username': Settings.get('email_smtp_username', ''),
        'smtp_password': Settings.get('email_smtp_password', ''),
        'imap_server': Settings.get('email_imap_server', 'imap.gmail.com'),
        'imap_port': Settings.get('email_imap_port', '993'),
        'imap_username': Settings.get('email_imap_username', ''),
        'imap_password': Settings.get('email_imap_password', ''),
        'monitor_email': Settings.get('email_monitor_email', '')
    }
    
    # Count photobooth photos
    photobooth_count = Photo.query.filter_by(is_photobooth=True).count()
    
    # Get email logs
    email_logs = EmailLog.query.order_by(EmailLog.received_at.desc()).limit(50).all()
    
    # Get Immich settings
    immich_settings = get_immich_settings()
    
    # Get Immich sync logs
    immich_sync_logs = ImmichSyncLog.query.order_by(ImmichSyncLog.sync_date.desc()).limit(50).all()
    
    # Get SSO settings
    sso_settings = get_sso_settings()
    
    # Get current user info if SSO is active
    current_user = None
    if session.get('sso_user_email'):
        current_user = {
            'email': session.get('sso_user_email'),
            'name': session.get('sso_user_name'),
            'domain': session.get('sso_user_domain')
        }
    
    return render_template('admin.html', 
                         photos=photos, 
                         total_photos=len(photos),
                         total_likes=total_likes,
                         total_comments=total_comments,
                         guestbook_entries=guestbook_entries,
                         total_guestbook=len(guestbook_entries),
                         visible_messages=visible_messages,
                         hidden_messages=hidden_messages,
                         total_messages=len(visible_messages),
                         total_message_comments=total_message_comments,
                         photobooth_count=photobooth_count,
                         public_url=public_url,
                         qr_settings=qr_settings,
                         welcome_settings=welcome_settings,
                         border_settings=border_settings,
                         timezone_settings=timezone_settings,
                         current_time=current_time,
                         email_settings=email_settings,
                         email_logs=email_logs,
                         immich_settings=immich_settings,
                         immich_sync_logs=immich_sync_logs,
                         sso_settings=sso_settings,
                         current_user=current_user)

@app.route('/admin/batch-download')
def batch_download():
    # Check for SSO session first
    sso_user_email = session.get('sso_user_email')
    sso_user_domain = session.get('sso_user_domain')
    admin_key = request.args.get('key', '')
    
    # Verify admin access
    if not verify_admin_access(admin_key, sso_user_email, sso_user_domain):
        return "Unauthorized", 401
    
    try:
        # Create a temporary zip file
        temp_dir = tempfile.mkdtemp()
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        zip_filename = f"wedding_gallery_backup_{timestamp}.zip"
        zip_path = os.path.join(temp_dir, zip_filename)
        
        with zipfile.ZipFile(zip_path, 'w', zipfile.ZIP_DEFLATED) as zipf:
            # Add all photos
            photos = Photo.query.all()
            for photo in photos:
                if photo.media_type == 'video':
                    file_path = os.path.join(app.config['VIDEO_FOLDER'], photo.filename)
                elif photo.is_photobooth:
                    file_path = os.path.join(app.config['PHOTOBOOTH_FOLDER'], photo.filename)
                else:
                    file_path = os.path.join(app.config['UPLOAD_FOLDER'], photo.filename)
                
                if os.path.exists(file_path):
                    # Create organized folder structure in zip
                    if photo.media_type == 'video':
                        zip_path_in_archive = f"videos/{photo.filename}"
                    elif photo.is_photobooth:
                        zip_path_in_archive = f"photobooth/{photo.filename}"
                    else:
                        zip_path_in_archive = f"photos/{photo.filename}"
                    
                    zipf.write(file_path, zip_path_in_archive)
                
                # Add video thumbnails if they exist
                if photo.media_type == 'video' and photo.thumbnail_filename:
                    thumb_path = os.path.join(app.config['THUMBNAIL_FOLDER'], photo.thumbnail_filename)
                    if os.path.exists(thumb_path):
                        zipf.write(thumb_path, f"video_thumbnails/{photo.thumbnail_filename}")
            
            # Add guestbook photos
            guestbook_entries = GuestbookEntry.query.all()
            for entry in guestbook_entries:
                if entry.photo_filename:
                    file_path = os.path.join(app.config['GUESTBOOK_UPLOAD_FOLDER'], entry.photo_filename)
                    if os.path.exists(file_path):
                        zipf.write(file_path, f"guestbook_photos/{entry.photo_filename}")
            
            # Add message board photos
            messages = Message.query.all()
            for message in messages:
                if message.photo_filename:
                    file_path = os.path.join(app.config['MESSAGE_UPLOAD_FOLDER'], message.photo_filename)
                    if os.path.exists(file_path):
                        zipf.write(file_path, f"message_photos/{message.photo_filename}")
            
            # Add border files
            border_settings = Settings.get('photobooth_border', '{}')
            border_settings = json.loads(border_settings) if border_settings else {}
            if border_settings.get('filename'):
                border_path = os.path.join(app.config['BORDER_FOLDER'], border_settings['filename'])
                if os.path.exists(border_path):
                    zipf.write(border_path, f"borders/{border_settings['filename']}")
            
            # Create and add a data export (JSON file with all database content)
            export_data = {
                'export_timestamp': datetime.now().isoformat(),
                'photos': [],
                'guestbook_entries': [],
                'messages': [],
                'settings': {}
            }
            
            # Export photos data
            for photo in photos:
                export_data['photos'].append({
                    'id': photo.id,
                    'filename': photo.filename,
                    'original_filename': photo.original_filename,
                    'uploader_name': photo.uploader_name,
                    'upload_date': photo.upload_date.isoformat(),
                    'description': photo.description,
                    'likes': photo.likes,
                    'media_type': photo.media_type,
                    'duration': photo.duration,
                    'is_photobooth': photo.is_photobooth,
                    'comments': [
                        {
                            'commenter_name': comment.commenter_name,
                            'content': comment.content,
                            'created_at': comment.created_at.isoformat()
                        } for comment in photo.comments
                    ]
                })
            
            # Export guestbook entries
            for entry in guestbook_entries:
                export_data['guestbook_entries'].append({
                    'id': entry.id,
                    'name': entry.name,
                    'message': entry.message,
                    'location': entry.location,
                    'photo_filename': entry.photo_filename,
                    'created_at': entry.created_at.isoformat()
                })
            
            # Export messages
            for message in messages:
                export_data['messages'].append({
                    'id': message.id,
                    'author_name': message.author_name,
                    'content': message.content,
                    'photo_filename': message.photo_filename,
                    'created_at': message.created_at.isoformat(),
                    'likes': message.likes,
                    'is_hidden': message.is_hidden,
                    'comments': [
                        {
                            'commenter_name': comment.commenter_name,
                            'content': comment.content,
                            'created_at': comment.created_at.isoformat(),
                            'is_hidden': comment.is_hidden
                        } for comment in message.message_comments
                    ]
                })
            
            # Export settings
            all_settings = Settings.query.all()
            for setting in all_settings:
                export_data['settings'][setting.key] = setting.value
            
            # Add the export data as JSON file
            import json
            export_json = json.dumps(export_data, indent=2, ensure_ascii=False)
            zipf.writestr('wedding_gallery_data_export.json', export_json)
        
        # Send the zip file
        return send_file(
            zip_path,
            mimetype='application/zip',
            as_attachment=True,
            download_name=zip_filename
        )
        
    except Exception as e:
        print(f"Error creating batch download: {e}")
        return f"Error creating download: {str(e)}", 500

@app.route('/admin/system-reset', methods=['POST'])
def system_reset():
    # Check for SSO session first
    sso_user_email = session.get('sso_user_email')
    sso_user_domain = session.get('sso_user_domain')
    admin_key = request.args.get('key', '')
    
    # Verify admin access
    if not verify_admin_access(admin_key, sso_user_email, sso_user_domain):
        return "Unauthorized", 401
    
    data = request.get_json()
    confirmation = data.get('confirmation', '')
    
    # Require specific confirmation text
    if confirmation != 'RESET EVERYTHING':
        return jsonify({'error': 'Invalid confirmation. Please type "RESET EVERYTHING" to confirm.'}), 400
    
    try:
        # Delete all database records
        MessageComment.query.delete()
        MessageLike.query.delete()
        Message.query.delete()
        Comment.query.delete()
        Like.query.delete()
        Photo.query.delete()
        GuestbookEntry.query.delete()
        Settings.query.delete()
        db.session.commit()
        
        # Delete all uploaded files
        upload_folders = [
            app.config['UPLOAD_FOLDER'],
            app.config['VIDEO_FOLDER'],
            app.config['THUMBNAIL_FOLDER'],
            app.config['PHOTOBOOTH_FOLDER'],
            app.config['GUESTBOOK_UPLOAD_FOLDER'],
            app.config['MESSAGE_UPLOAD_FOLDER'],
            app.config['BORDER_FOLDER']
        ]
        
        for folder in upload_folders:
            if os.path.exists(folder):
                # Remove all files in the folder
                for filename in os.listdir(folder):
                    file_path = os.path.join(folder, filename)
                    try:
                        if os.path.isfile(file_path):
                            os.unlink(file_path)
                    except Exception as e:
                        print(f"Error deleting {file_path}: {e}")
        
        return jsonify({'success': True, 'message': 'System reset completed successfully'})
        
    except Exception as e:
        db.session.rollback()
        print(f"Error during system reset: {e}")
        return jsonify({'error': f'System reset failed: {str(e)}'}), 500

@app.route('/admin/upload-border', methods=['POST'])
def upload_border():
    # Check for SSO session first
    sso_user_email = session.get('sso_user_email')
    sso_user_domain = session.get('sso_user_domain')
    admin_key = request.args.get('key', '')
    
    # Verify admin access
    if not verify_admin_access(admin_key, sso_user_email, sso_user_domain):
        return "Unauthorized", 401
    
    if 'border' not in request.files:
        return jsonify({'error': 'No file provided'}), 400
    
    file = request.files['border']
    if file.filename == '':
        return jsonify({'error': 'No file selected'}), 400
    
    if file and allowed_file(file.filename):
        # Remove old border file if exists
        border_settings = Settings.get('photobooth_border', '{}')
        border_settings = json.loads(border_settings) if border_settings else {}
        
        if border_settings.get('filename'):
            old_filepath = os.path.join(app.config['BORDER_FOLDER'], border_settings['filename'])
            if os.path.exists(old_filepath):
                os.remove(old_filepath)
        
        # Save new border
        filename = secure_filename(file.filename)
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        filename = f"border_{timestamp}_{filename}"
        filepath = os.path.join(app.config['BORDER_FOLDER'], filename)
        file.save(filepath)
        
        # Update settings
        border_settings = {
            'filename': filename,
            'border_url': url_for('static', filename=f'uploads/borders/{filename}')
        }
        Settings.set('photobooth_border', json.dumps(border_settings))
        
        return jsonify({
            'success': True,
            'border_url': border_settings['border_url']
        })
    
    return jsonify({'error': 'Invalid file type'}), 400

@app.route('/admin/delete/<int:photo_id>')
def delete_photo(photo_id):
    # Check for SSO session first
    sso_user_email = session.get('sso_user_email')
    sso_user_domain = session.get('sso_user_domain')
    admin_key = request.args.get('key', '')
    
    # Verify admin access
    if not verify_admin_access(admin_key, sso_user_email, sso_user_domain):
        return "Unauthorized", 401
    
    photo = Photo.query.get_or_404(photo_id)
    
    # Delete the file
    try:
        if photo.media_type == 'video':
            os.remove(os.path.join(app.config['VIDEO_FOLDER'], photo.filename))
            if photo.thumbnail_filename:
                os.remove(os.path.join(app.config['THUMBNAIL_FOLDER'], photo.thumbnail_filename))
        elif photo.is_photobooth:
            os.remove(os.path.join(app.config['PHOTOBOOTH_FOLDER'], photo.filename))
        else:
            os.remove(os.path.join(app.config['UPLOAD_FOLDER'], photo.filename))
    except:
        pass
    
    # Delete from database
    db.session.delete(photo)
    db.session.commit()
    
    return redirect(url_for('admin'))

@app.route('/admin/delete-guestbook/<int:entry_id>')
def delete_guestbook_entry(entry_id):
    # Check for SSO session first
    sso_user_email = session.get('sso_user_email')
    sso_user_domain = session.get('sso_user_domain')
    admin_key = request.args.get('key', '')
    
    # Verify admin access
    if not verify_admin_access(admin_key, sso_user_email, sso_user_domain):
        return "Unauthorized", 401
    
    entry = GuestbookEntry.query.get_or_404(entry_id)
    
    # Delete the photo file if exists
    if entry.photo_filename:
        try:
            os.remove(os.path.join(app.config['GUESTBOOK_UPLOAD_FOLDER'], entry.photo_filename))
        except:
            pass
    
    db.session.delete(entry)
    db.session.commit()
    
    return redirect(url_for('admin'))

@app.route('/admin/toggle-message/<int:message_id>')
def toggle_message_visibility(message_id):
    # Check for SSO session first
    sso_user_email = session.get('sso_user_email')
    sso_user_domain = session.get('sso_user_domain')
    admin_key = request.args.get('key', '')
    
    # Verify admin access
    if not verify_admin_access(admin_key, sso_user_email, sso_user_domain):
        return "Unauthorized", 401
    
    message = Message.query.get_or_404(message_id)
    message.is_hidden = not message.is_hidden
    db.session.commit()
    
    return redirect(url_for('admin'))

@app.route('/admin/delete-message/<int:message_id>')
def delete_message(message_id):
    # Check for SSO session first
    sso_user_email = session.get('sso_user_email')
    sso_user_domain = session.get('sso_user_domain')
    admin_key = request.args.get('key', '')
    
    # Verify admin access
    if not verify_admin_access(admin_key, sso_user_email, sso_user_domain):
        return "Unauthorized", 401
    
    message = Message.query.get_or_404(message_id)
    
    # Delete the photo file if exists
    if message.photo_filename:
        try:
            os.remove(os.path.join(app.config['MESSAGE_UPLOAD_FOLDER'], message.photo_filename))
        except:
            pass
    
    db.session.delete(message)
    db.session.commit()
    
    return redirect(url_for('admin'))

@app.route('/admin/toggle-message-comment/<int:comment_id>')
def toggle_message_comment_visibility(comment_id):
    # Check for SSO session first
    sso_user_email = session.get('sso_user_email')
    sso_user_domain = session.get('sso_user_domain')
    admin_key = request.args.get('key', '')
    
    # Verify admin access
    if not verify_admin_access(admin_key, sso_user_email, sso_user_domain):
        return "Unauthorized", 401
    
    comment = MessageComment.query.get_or_404(comment_id)
    comment.is_hidden = not comment.is_hidden
    db.session.commit()
    
    return redirect(url_for('admin'))

@app.route('/admin/delete-message-comment/<int:comment_id>')
def delete_message_comment(comment_id):
    # Check for SSO session first
    sso_user_email = session.get('sso_user_email')
    sso_user_domain = session.get('sso_user_domain')
    admin_key = request.args.get('key', '')
    
    # Verify admin access
    if not verify_admin_access(admin_key, sso_user_email, sso_user_domain):
        return "Unauthorized", 401
    
    comment = MessageComment.query.get_or_404(comment_id)
    db.session.delete(comment)
    db.session.commit()
    
    return redirect(url_for('admin'))

@app.route('/admin/edit-guestbook/<int:entry_id>', methods=['POST'])
def edit_guestbook_entry(entry_id):
    # Check for SSO session first
    sso_user_email = session.get('sso_user_email')
    sso_user_domain = session.get('sso_user_domain')
    admin_key = request.args.get('key', '')
    
    # Verify admin access
    if not verify_admin_access(admin_key, sso_user_email, sso_user_domain):
        return "Unauthorized", 401
    
    entry = GuestbookEntry.query.get_or_404(entry_id)
    data = request.get_json()
    
    entry.name = data.get('name', entry.name)
    entry.message = data.get('message', entry.message)
    entry.location = data.get('location', entry.location)
    
    db.session.commit()
    
    return jsonify({'success': True})

@app.route('/admin/save-settings', methods=['POST'])
def save_settings():
    # Check for SSO session first
    sso_user_email = session.get('sso_user_email')
    sso_user_domain = session.get('sso_user_domain')
    admin_key = request.args.get('key', '')
    
    # Verify admin access
    if not verify_admin_access(admin_key, sso_user_email, sso_user_domain):
        return "Unauthorized", 401
    
    data = request.get_json()
    
    # Save public URL
    if 'public_url' in data:
        Settings.set('public_url', data['public_url'])
    
    # Save QR settings
    if 'qr_settings' in data:
        Settings.set('qr_settings', json.dumps(data['qr_settings']))
    
    # Save welcome modal settings
    if 'welcome_settings' in data:
        Settings.set('welcome_modal', json.dumps(data['welcome_settings']))
    
    # Save email settings
    if 'email_settings' in data:
        email_data = data['email_settings']
        Settings.set('email_enabled', str(email_data.get('enabled', False)).lower())
        Settings.set('email_smtp_server', email_data.get('smtp_server', 'smtp.gmail.com'))
        Settings.set('email_smtp_port', str(email_data.get('smtp_port', '587')))
        Settings.set('email_smtp_username', email_data.get('smtp_username', ''))
        Settings.set('email_smtp_password', email_data.get('smtp_password', ''))
        Settings.set('email_imap_server', email_data.get('imap_server', 'imap.gmail.com'))
        Settings.set('email_imap_port', str(email_data.get('imap_port', '993')))
        Settings.set('email_imap_username', email_data.get('imap_username', ''))
        Settings.set('email_imap_password', email_data.get('imap_password', ''))
        Settings.set('email_monitor_email', email_data.get('monitor_email', ''))
    
    # Save Immich settings
    if 'immich_settings' in data:
        immich_data = data['immich_settings']
        Settings.set('immich_enabled', str(immich_data.get('enabled', False)).lower())
        Settings.set('immich_server_url', immich_data.get('server_url', ''))
        Settings.set('immich_api_key', immich_data.get('api_key', ''))
        Settings.set('immich_user_id', immich_data.get('user_id', ''))
        Settings.set('immich_album_name', immich_data.get('album_name', 'Wedding Gallery'))
        Settings.set('immich_sync_photos', str(immich_data.get('sync_photos', True)).lower())
        Settings.set('immich_sync_videos', str(immich_data.get('sync_videos', True)).lower())
        Settings.set('immich_sync_guestbook', str(immich_data.get('sync_guestbook', True)).lower())
        Settings.set('immich_sync_messages', str(immich_data.get('sync_messages', True)).lower())
        Settings.set('immich_sync_photobooth', str(immich_data.get('sync_photobooth', True)).lower())
    
    # Save SSO settings
    if 'sso_settings' in data:
        sso_data = data['sso_settings']
        Settings.set('sso_enabled', str(sso_data.get('enabled', False)).lower())
        Settings.set('sso_provider', sso_data.get('provider', 'google'))
        Settings.set('sso_client_id', sso_data.get('client_id', ''))
        Settings.set('sso_client_secret', sso_data.get('client_secret', ''))
        Settings.set('sso_authorization_url', sso_data.get('authorization_url', ''))
        Settings.set('sso_token_url', sso_data.get('token_url', ''))
        Settings.set('sso_userinfo_url', sso_data.get('userinfo_url', ''))
        Settings.set('sso_redirect_uri', sso_data.get('redirect_uri', ''))
        Settings.set('sso_scope', sso_data.get('scope', 'openid email profile'))
        Settings.set('sso_allowed_domains', ','.join(sso_data.get('allowed_domains', [])))
        Settings.set('sso_allowed_emails', ','.join(sso_data.get('allowed_emails', [])))
        Settings.set('sso_admin_key_fallback', str(sso_data.get('admin_key_fallback', True)).lower())
    
    # Save timezone settings
    if 'timezone_settings' in data:
        timezone_data = data['timezone_settings']
        Settings.set('timezone_settings', json.dumps(timezone_data))
    
    return jsonify({'success': True})

@app.route('/admin/start-email-monitor', methods=['POST'])
def start_email_monitor_route():
    # Check for SSO session first
    sso_user_email = session.get('sso_user_email')
    sso_user_domain = session.get('sso_user_domain')
    admin_key = request.args.get('key', '')
    
    # Verify admin access
    if not verify_admin_access(admin_key, sso_user_email, sso_user_domain):
        return "Unauthorized", 401
    
    try:
        email_settings = get_email_settings()
        if not email_settings['enabled']:
            return jsonify({'success': False, 'message': 'Email monitoring is disabled'})
        if not email_settings['imap_username']:
            return jsonify({'success': False, 'message': 'IMAP username not configured'})
        if not email_settings['imap_password']:
            return jsonify({'success': False, 'message': 'IMAP password not configured'})
            
        start_email_monitor()
        return jsonify({'success': True, 'message': 'Email monitor started successfully'})
    except Exception as e:
        return jsonify({'success': False, 'message': f'Error starting email monitor: {str(e)}'})

@app.route('/admin/check-email-settings', methods=['GET'])
def check_email_settings_route():
    # Check for SSO session first
    sso_user_email = session.get('sso_user_email')
    sso_user_domain = session.get('sso_user_domain')
    admin_key = request.args.get('key', '')
    
    # Verify admin access
    if not verify_admin_access(admin_key, sso_user_email, sso_user_domain):
        return jsonify({'success': False, 'message': 'Unauthorized'}), 401
    
    try:
        email_settings = get_email_settings()
        return jsonify({
            'success': True,
            'settings': {
                'enabled': email_settings['enabled'],
                'imap_server': email_settings['imap_server'],
                'imap_port': email_settings['imap_port'],
                'imap_username': email_settings['imap_username'],
                'imap_password_set': bool(email_settings['imap_password']),
                'smtp_server': email_settings['smtp_server'],
                'smtp_port': email_settings['smtp_port'],
                'smtp_username': email_settings['smtp_username'],
                'smtp_password_set': bool(email_settings['smtp_password'])
            }
        })
    except Exception as e:
        return jsonify({'success': False, 'message': f'Error checking email settings: {str(e)}'})

@app.route('/admin/process-emails', methods=['POST'])
def process_emails_route():
    # Check for SSO session first
    sso_user_email = session.get('sso_user_email')
    sso_user_domain = session.get('sso_user_domain')
    admin_key = request.args.get('key', '')
    
    # Verify admin access
    if not verify_admin_access(admin_key, sso_user_email, sso_user_domain):
        return jsonify({'success': False, 'message': 'Unauthorized'}), 401
    
    try:
        process_email_photos()
        return jsonify({'success': True, 'message': 'Email processing completed'})
    except Exception as e:
        return jsonify({'success': False, 'message': f'Error processing emails: {str(e)}'})

@app.route('/admin/sync-immich', methods=['POST'])
def sync_immich_route():
    # Check for SSO session first
    sso_user_email = session.get('sso_user_email')
    sso_user_domain = session.get('sso_user_domain')
    admin_key = request.args.get('key', '')
    
    # Verify admin access
    if not verify_admin_access(admin_key, sso_user_email, sso_user_domain):
        return jsonify({'success': False, 'message': 'Unauthorized'}), 401
    
    try:
        result = sync_all_to_immich()
        return jsonify({'success': True, 'message': result})
    except Exception as e:
        return jsonify({'success': False, 'message': str(e)})

@app.route('/admin/notification-users')
def notification_users():
    # Check for SSO session first
    sso_user_email = session.get('sso_user_email')
    sso_user_domain = session.get('sso_user_domain')
    admin_key = request.args.get('key', '')
    
    # Verify admin access
    if not verify_admin_access(admin_key, sso_user_email, sso_user_domain):
        return "Unauthorized", 401
    
    users = NotificationUser.query.order_by(NotificationUser.last_seen.desc()).all()
    return render_template('notification_users.html', users=users, admin_key=admin_key)

@app.route('/admin/send-notification', methods=['POST'])
def send_admin_notification():
    # Check for SSO session first
    sso_user_email = session.get('sso_user_email')
    sso_user_domain = session.get('sso_user_domain')
    admin_key = request.args.get('key', '')
    
    # Verify admin access
    if not verify_admin_access(admin_key, sso_user_email, sso_user_domain):
        return jsonify({'success': False, 'message': 'Unauthorized'}), 401
    
    try:
        data = request.get_json()
        notification_type = data.get('type', 'mass')  # 'mass' or 'individual'
        title = data.get('title', '')
        message = data.get('message', '')
        user_identifier = data.get('user_identifier', '')  # For individual notifications
        
        if not title or not message:
            return jsonify({'success': False, 'message': 'Title and message are required'})
        
        if notification_type == 'individual':
            # Send to specific user
            if not user_identifier:
                return jsonify({'success': False, 'message': 'User identifier required for individual notification'})
            
            user = NotificationUser.query.filter_by(user_identifier=user_identifier).first()
            if not user:
                return jsonify({'success': False, 'message': 'User not found'})
            
            # Create notification in database
            notification = Notification(
                user_identifier=user_identifier,
                title=title,
                message=message,
                notification_type='admin'
            )
            db.session.add(notification)
            db.session.commit()
            
            # The frontend will pick this up when it polls for notifications
            return jsonify({'success': True, 'message': f'Notification sent to {user.user_name}'})
        
        else:
            # Send mass notification
            users = NotificationUser.query.filter_by(notifications_enabled=True).all()
            sent_count = 0
            
            for user in users:
                # Create notification in database for each user
                notification = Notification(
                    user_identifier=user.user_identifier,
                    title=title,
                    message=message,
                    notification_type='admin'
                )
                db.session.add(notification)
                sent_count += 1
            
            db.session.commit()
            
            return jsonify({
                'success': True, 
                'message': f'Mass notification sent to {sent_count} users'
            })
    
    except Exception as e:
        print(f"Error sending notification: {e}")
        db.session.rollback()
        return jsonify({'success': False, 'message': str(e)})

@app.route('/admin/generate-qr-pdf')
def generate_qr_pdf():
    # Check for SSO session first
    sso_user_email = session.get('sso_user_email')
    sso_user_domain = session.get('sso_user_domain')
    admin_key = request.args.get('key', '')
    
    # Verify admin access
    if not verify_admin_access(admin_key, sso_user_email, sso_user_domain):
        return "Unauthorized", 401
    
    public_url = Settings.get('public_url', '')
    if not public_url:
        return "No public URL set", 400
    
    qr_settings = Settings.get('qr_settings', '{}')
    qr_settings = json.loads(qr_settings) if qr_settings else {}
    
    # Get email settings for the welcome modal
    email_settings = get_email_settings()
    monitor_email = email_settings.get('monitor_email', 'your-email@example.com')
    
    # Default settings
    title = qr_settings.get('title', 'Share Your Wedding Photos!')
    subtitle = qr_settings.get('subtitle', 'Scan to Upload & View Photos')
    message = qr_settings.get('message', 'We would love to see the wedding through your eyes! Please scan the QR code below to upload your photos and view the gallery.')
    couple_names = qr_settings.get('couple_names', 'The Happy Couple')
    
    # Create QR code
    qr = qrcode.QRCode(version=1, box_size=10, border=5)
    qr.add_data(public_url)
    qr.make(fit=True)
    qr_img = qr.make_image(fill_color="black", back_color="white")
    
    # Save QR code to BytesIO
    qr_buffer = BytesIO()
    qr_img.save(qr_buffer, format='PNG')
    qr_buffer.seek(0)
    
    # Create PDF
    pdf_buffer = BytesIO()
    doc = SimpleDocTemplate(pdf_buffer, pagesize=letter, topMargin=1*inch, bottomMargin=1*inch)
    
    # Styles
    styles = getSampleStyleSheet()
    
    # Custom styles
    title_style = ParagraphStyle(
        'CustomTitle',
        parent=styles['Heading1'],
        fontSize=28,
        textColor=colors.HexColor('#8b7355'),
        spaceAfter=8,
        alignment=TA_CENTER,
        fontName='Helvetica-Bold'
    )
    
    subtitle_style = ParagraphStyle(
        'CustomSubtitle',
        parent=styles['Heading2'],
        fontSize=16,
        textColor=colors.HexColor('#6b5d54'),
        spaceAfter=20,
        alignment=TA_CENTER,
        fontName='Helvetica'
    )
    
    body_style = ParagraphStyle(
        'CustomBody',
        parent=styles['BodyText'],
        fontSize=12,
        textColor=colors.HexColor('#444444'),
        alignment=TA_CENTER,
        spaceAfter=20,
        leading=16
    )
    
    couple_style = ParagraphStyle(
        'CoupleNames',
        parent=styles['BodyText'],
        fontSize=14,
        textColor=colors.HexColor('#8b7355'),
        alignment=TA_CENTER,
        fontName='Helvetica-Oblique'
    )
    
    url_style = ParagraphStyle(
        'URLStyle',
        parent=styles['BodyText'],
        fontSize=10,
        textColor=colors.HexColor('#666666'),
        alignment=TA_CENTER,
        spaceAfter=15
    )
    
    # Build PDF content
    story = []
    
    # Title
    story.append(Paragraph(title, title_style))
    story.append(Paragraph(subtitle, subtitle_style))
    
    # Message (shorter version)
    story.append(Paragraph(message, body_style))
    
    # Email instructions (condensed)
    email_instructions = f"""
    <b>📧 Email Photos:</b> Send to <b>{monitor_email}</b><br/>
    <i>Only photos (JPG, PNG, GIF, WebP) accepted</i>
    """
    story.append(Paragraph(email_instructions, body_style))
    story.append(Spacer(1, 0.2*inch))
    
    # QR Code
    qr_image = Image(qr_buffer, width=2.5*inch, height=2.5*inch)
    qr_image.hAlign = 'CENTER'
    story.append(qr_image)
    
    story.append(Spacer(1, 0.2*inch))
    
    # URL
    story.append(Paragraph(f"<i>{public_url}</i>", url_style))
    
    # Couple names
    story.append(Paragraph(f"With love,<br/>{couple_names}", couple_style))
    
    # Add decorative elements
    decoration = Table([['❤️ ❤️ ❤️']], colWidths=[6*inch])
    decoration.setStyle(TableStyle([
        ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
        ('FONTNAME', (0, 0), (-1, -1), 'Helvetica'),
        ('FONTSIZE', (0, 0), (-1, -1), 16),
        ('TEXTCOLOR', (0, 0), (-1, -1), colors.HexColor('#8b7355')),
    ]))
    story.append(Spacer(1, 0.3*inch))
    story.append(decoration)
    
    # Build PDF
    doc.build(story)
    
    pdf_buffer.seek(0)
    
    return send_file(
        pdf_buffer,
        mimetype='application/pdf',
        as_attachment=True,
        download_name='wedding_photo_qr.pdf'
    )



@app.route('/admin/pwa-debug')
def pwa_debug():
    # Check for SSO session first
    sso_user_email = session.get('sso_user_email')
    sso_user_domain = session.get('sso_user_domain')
    admin_key = request.args.get('key', '')
    
    # Verify admin access
    if not verify_admin_access(admin_key, sso_user_email, sso_user_domain):
        return "Unauthorized", 401
    
    # Check PWA requirements
    debug_info = {
        'https': request.is_secure,
        'host': request.host,
        'url': request.url,
        'manifest_exists': os.path.exists('static/manifest.json'),
        'sw_exists': os.path.exists('static/sw.js'),
        'icons_exist': all(os.path.exists(f'static/icons/icon-{size}x{size}.png') 
                         for size in [192, 512]),
        'user_agent': request.headers.get('User-Agent', ''),
        'accept_language': request.headers.get('Accept-Language', ''),
    }
    
    return render_template('pwa_debug.html', debug_info=debug_info)

@app.route('/privacy-policy')
def privacy_policy():
    current_date = datetime.now().strftime('%B %d, %Y')
    return render_template('privacy_policy.html', current_date=current_date)

@app.route('/terms-of-use')
def terms_of_use():
    current_date = datetime.now().strftime('%B %d, %Y')
    return render_template('terms_of_use.html', current_date=current_date)

@app.errorhandler(413)
def too_large(e):
    log_error('system', 'File upload too large', details={'error': '413', 'max_size': app.config['MAX_CONTENT_LENGTH']})
    return "File is too large. Maximum size is 50MB.", 413

@app.errorhandler(404)
def not_found(e):
    log_error('system', 'Page not found', details={'path': request.path, 'method': request.method})
    return "Page not found", 404

@app.errorhandler(500)
def internal_error(e):
    log_critical('system', 'Internal server error', details={'path': request.path, 'method': request.method})
    return "Internal server error", 500

@app.route('/api/notifications/check')
def check_notifications():
    """Check for new notifications for the current user"""
    user_identifier = request.cookies.get('user_identifier', '')
    if not user_identifier:
        return jsonify({'notifications': []})
    
    try:
        # Get unread notifications for this user
        notifications = Notification.query.filter_by(
            user_identifier=user_identifier,
            is_read=False
        ).order_by(Notification.created_at.desc()).all()
        
        notification_list = []
        for notification in notifications:
            # Use getattr to safely access columns that might not exist yet
            notification_list.append({
                'id': notification.id,
                'title': notification.title,
                'message': notification.message,
                'type': notification.notification_type,
                'created_at': notification.created_at.strftime('%B %d, %Y at %I:%M %p'),
                'is_read': notification.is_read,
                'content_type': getattr(notification, 'content_type', None),
                'content_id': getattr(notification, 'content_id', None)
            })
        
        print(f"Found {len(notification_list)} unread notifications for user {user_identifier}")
        return jsonify({'notifications': notification_list})
        
    except Exception as e:
        print(f"Error checking notifications: {e}")
        # Return empty list if there's an error (e.g., missing columns)
        return jsonify({'notifications': []})

@app.route('/api/notifications/mark-read', methods=['POST'])
def mark_notification_read():
    """Mark a notification as read"""
    user_identifier = request.cookies.get('user_identifier', '')
    if not user_identifier:
        return jsonify({'success': False, 'message': 'User not authenticated'})
    
    data = request.get_json()
    notification_id = data.get('notification_id')
    
    if not notification_id:
        return jsonify({'success': False, 'message': 'Notification ID required'})
    
    try:
        notification = Notification.query.filter_by(
            id=notification_id,
            user_identifier=user_identifier
        ).first()
        
        if notification:
            notification.is_read = True
            notification.read_at = datetime.utcnow()
            db.session.commit()
            return jsonify({'success': True})
        else:
            return jsonify({'success': False, 'message': 'Notification not found'})
    
    except Exception as e:
        return jsonify({'success': False, 'message': str(e)})

@app.route('/api/notifications/mark-all-read', methods=['POST'])
def mark_all_notifications_read():
    """Mark all notifications as read for the current user"""
    user_identifier = request.cookies.get('user_identifier', '')
    if not user_identifier:
        return jsonify({'success': False, 'message': 'User not authenticated'})
    
    try:
        notifications = Notification.query.filter_by(
            user_identifier=user_identifier,
            is_read=False
        ).all()
        
        for notification in notifications:
            notification.is_read = True
            notification.read_at = datetime.utcnow()
        
        db.session.commit()
        return jsonify({'success': True, 'message': f'Marked {len(notifications)} notifications as read'})
    
    except Exception as e:
        return jsonify({'success': False, 'message': str(e)})

@app.route('/notifications')
def notifications_page():
    """Notifications page for users"""
    return render_template('notifications.html')

@app.route('/api/notifications/delete', methods=['POST'])
def delete_notification():
    """Delete a notification"""
    user_identifier = request.cookies.get('user_identifier', '')
    if not user_identifier:
        return jsonify({'success': False, 'message': 'User not authenticated'})
    
    data = request.get_json()
    notification_id = data.get('notification_id')
    
    if not notification_id:
        return jsonify({'success': False, 'message': 'Notification ID required'})
    
    try:
        notification = Notification.query.filter_by(
            id=notification_id,
            user_identifier=user_identifier
        ).first()
        
        if notification:
            db.session.delete(notification)
            db.session.commit()
            return jsonify({'success': True})
        else:
            return jsonify({'success': False, 'message': 'Notification not found'})
    
    except Exception as e:
        return jsonify({'success': False, 'message': str(e)})

# SSO routes are handled by the auth blueprint

@app.route('/admin/register-notification-user', methods=['POST'])
def register_notification_user():
    """Register a user for notifications"""
    data = request.get_json()
    user_identifier = data.get('user_identifier', '')
    user_name = data.get('user_name', 'Anonymous')
    device_info = data.get('device_info', '')
    notifications_enabled = data.get('notifications_enabled', True)
    
    if not user_identifier:
        return jsonify({'success': False, 'message': 'User identifier required'})
    
    try:
        # Find or create notification user
        notification_user = NotificationUser.query.filter_by(
            user_identifier=user_identifier
        ).first()
        
        if notification_user:
            # Update existing user
            notification_user.user_name = user_name
            notification_user.notifications_enabled = notifications_enabled
            notification_user.last_seen = datetime.utcnow()
            notification_user.device_info = device_info
        else:
            # Create new notification user
            notification_user = NotificationUser(
                user_identifier=user_identifier,
                user_name=user_name,
                notifications_enabled=notifications_enabled,
                last_seen=datetime.utcnow(),
                device_info=device_info
            )
            db.session.add(notification_user)
        
        db.session.commit()
        
        return jsonify({
            'success': True, 
            'message': f'User registered for notifications successfully'
        })
    
    except Exception as e:
        print(f"Error registering notification user: {e}")
        return jsonify({'success': False, 'message': str(e)})

@app.route('/api/notifications/toggle-enabled', methods=['POST'])
def toggle_notifications_enabled():
    """Toggle notification settings for a user"""
    user_identifier = request.cookies.get('user_identifier', '')
    if not user_identifier:
        return jsonify({'success': False, 'message': 'User not authenticated'})
    
    data = request.get_json()
    enabled = data.get('enabled', True)
    
    try:
        # Find or create notification user
        notification_user = NotificationUser.query.filter_by(
            user_identifier=user_identifier
        ).first()
        
        if notification_user:
            notification_user.notifications_enabled = enabled
            notification_user.last_seen = datetime.utcnow()
        else:
            # Create new notification user
            user_name = request.cookies.get('user_name', 'Anonymous')
            notification_user = NotificationUser(
                user_identifier=user_identifier,
                user_name=user_name,
                notifications_enabled=enabled,
                last_seen=datetime.utcnow()
            )
            db.session.add(notification_user)
        
        db.session.commit()
        
        return jsonify({
            'success': True, 
            'message': f'Notifications {"enabled" if enabled else "disabled"} successfully'
        })
    
    except Exception as e:
        return jsonify({'success': False, 'message': str(e)})

def trigger_push_notification(user_identifier, title, message, notification_type='admin'):
    """Trigger a push notification for a specific user"""
    try:
        # Check if user has notifications enabled
        user = NotificationUser.query.filter_by(
            user_identifier=user_identifier,
            notifications_enabled=True
        ).first()
        
        if user:
            print(f"Push notification triggered for {user.user_name}: {title} - {message}")
            # The actual push notification will be handled by the frontend
            # when it checks for new notifications
            return True
        else:
            print(f"User {user_identifier} not found or notifications disabled")
            return False
    except Exception as e:
        print(f"Error triggering push notification: {e}")
        return False

def create_notification_with_push(user_identifier, title, message, notification_type='admin', content_type=None, content_id=None):
    """Create a notification in database and trigger push notification"""
    try:
        # Create notification in database
        notification = Notification(
            user_identifier=user_identifier,
            title=title,
            message=message,
            notification_type=notification_type,
            content_type=content_type,
            content_id=content_id
        )
        db.session.add(notification)
        db.session.commit()
        
        print(f"Database notification created for {user_identifier}: {title} - {message}")
        
        # Trigger push notification
        trigger_push_notification(user_identifier, title, message, notification_type)
        
        return notification
    except Exception as e:
        print(f"Error creating notification: {e}")
        return None

@app.route('/test-notification')
def test_notification():
    """Test route to create a notification for the current user"""
    user_identifier = request.cookies.get('user_identifier', '')
    if not user_identifier:
        return jsonify({'error': 'No user identifier found'})
    
    # Create a test notification
    notification = create_notification_with_push(
        user_identifier=user_identifier,
        title='🧪 Test Notification',
        message='This is a test notification to verify the system is working!',
        notification_type='admin'
    )
    
    if notification:
        return jsonify({
            'success': True,
            'message': 'Test notification created successfully',
            'notification_id': notification.id
        })
    else:
        return jsonify({
            'success': False,
            'message': 'Failed to create test notification'
        })

@app.route('/debug/notification-users')
def debug_notification_users():
    """Debug route to show notification users and their unread counts"""
    try:
        users = NotificationUser.query.all()
        result = []
        for user in users:
            unread_count = Notification.query.filter_by(
                user_identifier=user.user_identifier,
                is_read=False
            ).count()
            result.append({
                'user_identifier': user.user_identifier,
                'user_name': user.user_name,
                'notifications_enabled': user.notifications_enabled,
                'unread_count': unread_count,
                'last_seen': user.last_seen.isoformat() if user.last_seen else None
            })
        return jsonify({'users': result})
    except Exception as e:
        return jsonify({'error': str(e)})

@app.route('/debug/push-notification-test')
def debug_push_notification_test():
    """Debug route to test push notifications"""
    user_identifier = request.cookies.get('user_identifier', '')
    if not user_identifier:
        return jsonify({'error': 'No user identifier found'})
    
    try:
        # Create a test notification
        notification = create_notification_with_push(
            user_identifier=user_identifier,
            title='🧪 Test Push Notification',
            message='This is a test push notification to verify the system is working!',
            notification_type='test',
            content_type='photo',
            content_id=1
        )
        
        if notification:
            return jsonify({
                'success': True,
                'message': 'Test push notification created successfully',
                'notification_id': notification.id,
                'user_identifier': user_identifier
            })
        else:
            return jsonify({
                'success': False,
                'message': 'Failed to create test notification'
            })
    except Exception as e:
        return jsonify({
            'success': False,
            'message': f'Error creating test notification: {str(e)}'
        })



if __name__ == '__main__':
    with app.app_context():
        db.create_all()
        
        # Log application startup
        try:
            log_info('system', 'Application started successfully')
        except Exception as e:
            print(f"Failed to log application startup: {e}")
        
        # Start email monitor if enabled
        try:
            email_settings = get_email_settings()
            print(f"Email settings - Enabled: {email_settings['enabled']}, IMAP Username: {email_settings['imap_username']}, IMAP Password: {'*' * len(email_settings['imap_password']) if email_settings['imap_password'] else 'Not set'}")
            
            if email_settings['enabled'] and email_settings['imap_username'] and email_settings['imap_password']:
                start_email_monitor()
                print("Email monitor started successfully")
                log_info('email', 'Email monitor started successfully')
            else:
                print("Email monitor not started - not enabled or not configured")
                log_info('email', 'Email monitor not started - not enabled or not configured')
                if not email_settings['enabled']:
                    print("  - Email monitoring is disabled")
                if not email_settings['imap_username']:
                    print("  - IMAP username not configured")
                if not email_settings['imap_password']:
                    print("  - IMAP password not configured")
        except Exception as e:
            print(f"Email monitor not started: {e}")
            log_error('email', f'Email monitor failed to start: {e}')
    app.run(debug=True, host='0.0.0.0')