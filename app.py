from flask import Flask, render_template, request, redirect, url_for, jsonify, make_response, send_file
from flask_sqlalchemy import SQLAlchemy
from datetime import datetime
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

db = SQLAlchemy(app)

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
    upload_date = db.Column(db.DateTime, default=datetime.utcnow)
    description = db.Column(db.Text)
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

@app.route('/')
def index():
    photos = Photo.query.order_by(Photo.upload_date.desc()).all()
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
    
    return render_template('index.html', 
                         photos=photos, 
                         user_name=user_name,
                         welcome_settings=welcome_settings,
                         show_modal=show_modal)

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
                    description=description,
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
                    description=description,
                    media_type='image'
                )
            
            db.session.add(photo)
            db.session.commit()
            
            # Save user name in cookie
            resp = make_response(redirect(url_for('index')))
            resp.set_cookie('user_name', uploader_name, max_age=30*24*60*60)  # 30 days
            return resp
    
    user_name = request.cookies.get('user_name', '')
    return render_template('upload.html', user_name=user_name)

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
            
            photo = Photo(
                filename=filename,
                original_filename=filename,
                uploader_name=uploader_name,
                description=description,
                media_type='image',
                is_photobooth=True
            )
            
            db.session.add(photo)
            db.session.commit()
            
            # Save user name in cookie
            resp = jsonify({
                'success': True,
                'filename': filename,
                'uploaded': True,
                'photo_id': photo.id
            })
            resp.set_cookie('user_name', uploader_name, max_age=30*24*60*60)
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
                content=content,
                photo_filename=photo_filename
            )
            db.session.add(message)
            db.session.commit()
            
            # Save user name in cookie
            resp = make_response(redirect(url_for('message_board')))
            resp.set_cookie('user_name', author_name, max_age=30*24*60*60)  # 30 days
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
    
    resp = jsonify({'likes': message.likes, 'liked': liked})
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
    
    resp = jsonify({
        'id': comment.id,
        'commenter_name': comment.commenter_name,
        'content': comment.content,
        'created_at': comment.created_at.strftime('%B %d, %Y at %I:%M %p')
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
    
    resp = jsonify({'likes': photo.likes, 'liked': liked})
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
    
    resp = jsonify({
        'id': comment.id,
        'commenter_name': comment.commenter_name,
        'content': comment.content,
        'created_at': comment.created_at.strftime('%B %d, %Y at %I:%M %p')
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
    # Simple admin authentication - in production, use proper authentication
    admin_key = request.args.get('key', '')
    if admin_key != 'wedding2024':  # Change this to a secure key
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
    
    # Count photobooth photos
    photobooth_count = Photo.query.filter_by(is_photobooth=True).count()
    
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
                         border_settings=border_settings)

@app.route('/admin/batch-download')
def batch_download():
    admin_key = request.args.get('key', '')
    if admin_key != 'wedding2024':
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
    admin_key = request.args.get('key', '')
    if admin_key != 'wedding2024':
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
    admin_key = request.args.get('key', '')
    if admin_key != 'wedding2024':
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
    admin_key = request.args.get('key', '')
    if admin_key != 'wedding2024':  # Change this to a secure key
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
    
    return redirect(url_for('admin', key=admin_key))

@app.route('/admin/delete-guestbook/<int:entry_id>')
def delete_guestbook_entry(entry_id):
    admin_key = request.args.get('key', '')
    if admin_key != 'wedding2024':
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
    
    return redirect(url_for('admin', key=admin_key))

@app.route('/admin/toggle-message/<int:message_id>')
def toggle_message_visibility(message_id):
    admin_key = request.args.get('key', '')
    if admin_key != 'wedding2024':
        return "Unauthorized", 401
    
    message = Message.query.get_or_404(message_id)
    message.is_hidden = not message.is_hidden
    db.session.commit()
    
    return redirect(url_for('admin', key=admin_key))

@app.route('/admin/delete-message/<int:message_id>')
def delete_message(message_id):
    admin_key = request.args.get('key', '')
    if admin_key != 'wedding2024':
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
    
    return redirect(url_for('admin', key=admin_key))

@app.route('/admin/toggle-message-comment/<int:comment_id>')
def toggle_message_comment_visibility(comment_id):
    admin_key = request.args.get('key', '')
    if admin_key != 'wedding2024':
        return "Unauthorized", 401
    
    comment = MessageComment.query.get_or_404(comment_id)
    comment.is_hidden = not comment.is_hidden
    db.session.commit()
    
    return redirect(url_for('admin', key=admin_key))

@app.route('/admin/delete-message-comment/<int:comment_id>')
def delete_message_comment(comment_id):
    admin_key = request.args.get('key', '')
    if admin_key != 'wedding2024':
        return "Unauthorized", 401
    
    comment = MessageComment.query.get_or_404(comment_id)
    db.session.delete(comment)
    db.session.commit()
    
    return redirect(url_for('admin', key=admin_key))

@app.route('/admin/edit-guestbook/<int:entry_id>', methods=['POST'])
def edit_guestbook_entry(entry_id):
    admin_key = request.args.get('key', '')
    if admin_key != 'wedding2024':
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
    admin_key = request.args.get('key', '')
    if admin_key != 'wedding2024':
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
    
    return jsonify({'success': True})

@app.route('/admin/generate-qr-pdf')
def generate_qr_pdf():
    admin_key = request.args.get('key', '')
    if admin_key != 'wedding2024':
        return "Unauthorized", 401
    
    public_url = Settings.get('public_url', '')
    if not public_url:
        return "No public URL set", 400
    
    qr_settings = Settings.get('qr_settings', '{}')
    qr_settings = json.loads(qr_settings) if qr_settings else {}
    
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
        fontSize=36,
        textColor=colors.HexColor('#8b7355'),
        spaceAfter=12,
        alignment=TA_CENTER,
        fontName='Helvetica-Bold'
    )
    
    subtitle_style = ParagraphStyle(
        'CustomSubtitle',
        parent=styles['Heading2'],
        fontSize=20,
        textColor=colors.HexColor('#6b5d54'),
        spaceAfter=30,
        alignment=TA_CENTER,
        fontName='Helvetica'
    )
    
    body_style = ParagraphStyle(
        'CustomBody',
        parent=styles['BodyText'],
        fontSize=14,
        textColor=colors.HexColor('#444444'),
        alignment=TA_CENTER,
        spaceAfter=30,
        leading=20
    )
    
    couple_style = ParagraphStyle(
        'CoupleNames',
        parent=styles['BodyText'],
        fontSize=18,
        textColor=colors.HexColor('#8b7355'),
        alignment=TA_CENTER,
        fontName='Helvetica-Oblique'
    )
    
    url_style = ParagraphStyle(
        'URLStyle',
        parent=styles['BodyText'],
        fontSize=12,
        textColor=colors.HexColor('#666666'),
        alignment=TA_CENTER,
        spaceAfter=20
    )
    
    # Build PDF content
    story = []
    
    # Decorative line
    story.append(Spacer(1, 0.5*inch))
    
    # Title
    story.append(Paragraph(title, title_style))
    story.append(Paragraph(subtitle, subtitle_style))
    
    # Message
    story.append(Paragraph(message, body_style))
    
    # QR Code
    qr_image = Image(qr_buffer, width=3*inch, height=3*inch)
    qr_image.hAlign = 'CENTER'
    story.append(qr_image)
    
    story.append(Spacer(1, 0.3*inch))
    
    # URL
    story.append(Paragraph(f"<i>{public_url}</i>", url_style))
    
    story.append(Spacer(1, 0.5*inch))
    
    # Couple names
    story.append(Paragraph(f"With love,<br/>{couple_names}", couple_style))
    
    # Add decorative elements
    decoration = Table([['❤️ ❤️ ❤️']], colWidths=[6*inch])
    decoration.setStyle(TableStyle([
        ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
        ('FONTNAME', (0, 0), (-1, -1), 'Helvetica'),
        ('FONTSIZE', (0, 0), (-1, -1), 20),
        ('TEXTCOLOR', (0, 0), (-1, -1), colors.HexColor('#8b7355')),
    ]))
    story.append(Spacer(1, 0.5*inch))
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
    return "File is too large. Maximum size is 50MB.", 413

if __name__ == '__main__':
    with app.app_context():
        db.create_all()
    app.run(debug=True, host='0.0.0.0')