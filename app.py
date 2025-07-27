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

app = Flask(__name__)
app.config['SECRET_KEY'] = os.environ.get('SECRET_KEY', secrets.token_hex(16))
app.config['SQLALCHEMY_DATABASE_URI'] = os.environ.get('DATABASE_URL', 'sqlite:///wedding_photos.db')
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['UPLOAD_FOLDER'] = 'static/uploads'
app.config['GUESTBOOK_UPLOAD_FOLDER'] = 'static/uploads/guestbook'
app.config['MESSAGE_UPLOAD_FOLDER'] = 'static/uploads/messages'
app.config['MAX_CONTENT_LENGTH'] = 16 * 1024 * 1024  # 16MB max file size
app.config['ALLOWED_EXTENSIONS'] = {'png', 'jpg', 'jpeg', 'gif', 'webp'}

db = SQLAlchemy(app)

# Ensure upload directories exist
os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)
os.makedirs(app.config['GUESTBOOK_UPLOAD_FOLDER'], exist_ok=True)
os.makedirs(app.config['MESSAGE_UPLOAD_FOLDER'], exist_ok=True)

# Database Models
class Photo(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    filename = db.Column(db.String(255), nullable=False)
    original_filename = db.Column(db.String(255), nullable=False)
    uploader_name = db.Column(db.String(100), default='Anonymous')
    upload_date = db.Column(db.DateTime, default=datetime.utcnow)
    description = db.Column(db.Text)
    likes = db.Column(db.Integer, default=0)
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
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in app.config['ALLOWED_EXTENSIONS']

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
                'Click "Upload Photo" to share your pictures',
                'Browse the gallery to see all photos',
                'Click on any photo to like or comment',
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
            filename = f"{timestamp}_{filename}"
            filepath = os.path.join(app.config['UPLOAD_FOLDER'], filename)
            file.save(filepath)
            
            uploader_name = request.form.get('uploader_name', 'Anonymous').strip() or 'Anonymous'
            description = request.form.get('description', '')
            
            photo = Photo(
                filename=filename,
                original_filename=file.filename,
                uploader_name=uploader_name,
                description=description
            )
            db.session.add(photo)
            db.session.commit()
            
            # Save user name in cookie
            resp = make_response(redirect(url_for('index')))
            resp.set_cookie('user_name', uploader_name, max_age=30*24*60*60)  # 30 days
            return resp
    
    user_name = request.cookies.get('user_name', '')
    return render_template('upload.html', user_name=user_name)

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
                         public_url=public_url,
                         qr_settings=qr_settings,
                         welcome_settings=welcome_settings)

@app.route('/admin/delete/<int:photo_id>')
def delete_photo(photo_id):
    admin_key = request.args.get('key', '')
    if admin_key != 'wedding2024':  # Change this to a secure key
        return "Unauthorized", 401
    
    photo = Photo.query.get_or_404(photo_id)
    
    # Delete the file
    try:
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

@app.errorhandler(413)
def too_large(e):
    return "File is too large. Maximum size is 16MB.", 413

if __name__ == '__main__':
    with app.app_context():
        db.create_all()
    app.run(debug=True, host='0.0.0.0')