from flask import Blueprint, render_template, request, redirect, url_for, jsonify, send_file, session, current_app
from werkzeug.utils import secure_filename
from datetime import datetime
import json
import os
import tempfile
import zipfile
import qrcode
from io import BytesIO
from reportlab.lib.pagesizes import letter
from reportlab.lib import colors
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Image, Table, TableStyle
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import inch
from reportlab.lib.enums import TA_CENTER, TA_JUSTIFY, TA_LEFT
from app.models.photo import Photo, Comment, Like
from app.models.guestbook import GuestbookEntry
from app.models.messages import Message, MessageComment, MessageLike
from app.models.settings import Settings
from app.models.email import EmailLog, ImmichSyncLog
from app.models.notifications import NotificationUser, Notification
from app import db
from app.utils.settings_utils import verify_admin_access, get_email_settings, get_immich_settings, get_sso_settings
from app.utils.email_utils import start_email_monitor
from app.utils.immich_utils import sync_all_to_immich
from app.utils.notification_utils import create_notification_with_push
from app.utils.db_optimization import db_optimizer, get_photo_stats, maintenance_task
from app.utils.system_logger import log_info, log_error, log_exception

admin_bp = Blueprint('admin', __name__)

@admin_bp.route('/')
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
            return redirect(url_for('auth.sso_login'))
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
    
    # Count photobooth photos
    photobooth_count = Photo.query.filter_by(is_photobooth=True).count()
    
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
    
    # Get Immich settings
    immich_settings = get_immich_settings()
    
    return render_template('admin_dashboard.html',
                         photos=photos,
                         total_photos=len(photos),
                         total_likes=total_likes,
                         total_comments=total_comments,
                         guestbook_entries=guestbook_entries,
                         total_guestbook=len(guestbook_entries),
                         visible_messages=visible_messages,
                         hidden_messages=hidden_messages,
                         total_messages=len(all_messages),
                         total_message_comments=total_message_comments,
                         photobooth_count=photobooth_count,
                         email_settings=email_settings,
                         immich_settings=immich_settings)

@admin_bp.route('/dashboard')
def admin_dashboard():
    # Check for SSO session first
    sso_user_email = session.get('sso_user_email')
    sso_user_domain = session.get('sso_user_domain')
    admin_key = request.args.get('key', '')
    
    # Verify admin access
    if not verify_admin_access(admin_key, sso_user_email, sso_user_domain):
        # If SSO is enabled, redirect to SSO login
        sso_settings = get_sso_settings()
        if sso_settings['enabled']:
            return redirect(url_for('auth.sso_login'))
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
    
    # Count photobooth photos
    photobooth_count = Photo.query.filter_by(is_photobooth=True).count()
    
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
    
    # Get Immich settings
    immich_settings = get_immich_settings()
    
    return render_template('admin_dashboard.html',
                         photos=photos,
                         total_photos=len(photos),
                         total_likes=total_likes,
                         total_comments=total_comments,
                         guestbook_entries=guestbook_entries,
                         total_guestbook=len(guestbook_entries),
                         visible_messages=visible_messages,
                         hidden_messages=hidden_messages,
                         total_messages=len(all_messages),
                         total_message_comments=total_message_comments,
                         photobooth_count=photobooth_count,
                         email_settings=email_settings,
                         immich_settings=immich_settings)

@admin_bp.route('/photos')
def admin_photos():
    # Check for SSO session first
    sso_user_email = session.get('sso_user_email')
    sso_user_domain = session.get('sso_user_domain')
    admin_key = request.args.get('key', '')
    
    # Verify admin access
    if not verify_admin_access(admin_key, sso_user_email, sso_user_domain):
        return "Unauthorized", 401
    
    photos = Photo.query.order_by(Photo.upload_date.desc()).all()
    total_likes = sum(photo.likes for photo in photos)
    total_comments = Comment.query.count()
    photobooth_count = Photo.query.filter_by(is_photobooth=True).count()
    total_videos = Photo.query.filter_by(media_type='video').count()
    
    return render_template('admin_photos.html',
                         photos=photos,
                         total_photos=len(photos),
                         total_videos=total_videos,
                         total_likes=total_likes,
                         total_comments=total_comments,
                         photobooth_count=photobooth_count)

@admin_bp.route('/email-settings')
def admin_email_settings():
    # Check for SSO session first
    sso_user_email = session.get('sso_user_email')
    sso_user_domain = session.get('sso_user_domain')
    admin_key = request.args.get('key', '')
    
    # Verify admin access
    if not verify_admin_access(admin_key, sso_user_email, sso_user_domain):
        return "Unauthorized", 401
    
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
    
    # Get email logs
    email_logs = EmailLog.query.order_by(EmailLog.received_at.desc()).limit(50).all()
    
    return render_template('admin_email_settings.html',
                         email_settings=email_settings,
                         email_logs=email_logs)

@admin_bp.route('/immich-settings')
def admin_immich_settings():
    # Check for SSO session first
    sso_user_email = session.get('sso_user_email')
    sso_user_domain = session.get('sso_user_domain')
    admin_key = request.args.get('key', '')
    
    # Verify admin access
    if not verify_admin_access(admin_key, sso_user_email, sso_user_domain):
        return "Unauthorized", 401
    
    # Get Immich settings
    immich_settings = get_immich_settings()
    
    # Get Immich sync logs
    immich_sync_logs = ImmichSyncLog.query.order_by(ImmichSyncLog.sync_date.desc()).limit(50).all()
    
    return render_template('admin_immich_settings.html',
                         immich_settings=immich_settings,
                         immich_sync_logs=immich_sync_logs)

@admin_bp.route('/guestbook')
def admin_guestbook():
    # Check for SSO session first
    sso_user_email = session.get('sso_user_email')
    sso_user_domain = session.get('sso_user_domain')
    admin_key = request.args.get('key', '')
    
    # Verify admin access
    if not verify_admin_access(admin_key, sso_user_email, sso_user_domain):
        return "Unauthorized", 401
    
    # Get guestbook entries
    guestbook_entries = GuestbookEntry.query.order_by(GuestbookEntry.created_at.desc()).all()
    
    # Calculate statistics
    total_entries = len(guestbook_entries)
    entries_with_photos = len([e for e in guestbook_entries if e.photo_filename])
    entries_with_location = len([e for e in guestbook_entries if e.location])
    
    # Count recent entries (last 7 days)
    from datetime import datetime, timedelta
    week_ago = datetime.now() - timedelta(days=7)
    recent_entries = len([e for e in guestbook_entries if e.created_at >= week_ago])
    
    return render_template('admin_guestbook.html',
                         guestbook_entries=guestbook_entries,
                         total_entries=total_entries,
                         entries_with_photos=entries_with_photos,
                         entries_with_location=entries_with_location,
                         recent_entries=recent_entries)

@admin_bp.route('/messages')
def admin_messages():
    # Check for SSO session first
    sso_user_email = session.get('sso_user_email')
    sso_user_domain = session.get('sso_user_domain')
    admin_key = request.args.get('key', '')
    
    # Verify admin access
    if not verify_admin_access(admin_key, sso_user_email, sso_user_domain):
        return "Unauthorized", 401
    
    # Get messages
    all_messages = Message.query.order_by(Message.created_at.desc()).all()
    visible_messages = [m for m in all_messages if not m.is_hidden]
    hidden_messages = [m for m in all_messages if m.is_hidden]
    
    # Calculate statistics
    total_messages = len(all_messages)
    total_comments = MessageComment.query.count()
    messages_with_photos = len([m for m in all_messages if m.photo_filename])
    
    return render_template('admin_messages.html',
                         visible_messages=visible_messages,
                         hidden_messages=hidden_messages,
                         total_messages=total_messages,
                         total_comments=total_comments,
                         messages_with_photos=messages_with_photos)

@admin_bp.route('/photobooth')
def admin_photobooth():
    # Check for SSO session first
    sso_user_email = session.get('sso_user_email')
    sso_user_domain = session.get('sso_user_domain')
    admin_key = request.args.get('key', '')
    
    # Verify admin access
    if not verify_admin_access(admin_key, sso_user_email, sso_user_domain):
        return "Unauthorized", 401
    
    # Get photobooth settings
    border_settings_json = Settings.get('photobooth_border', '{}')
    border_settings = json.loads(border_settings_json) if border_settings_json else {}
    
    # Get photobooth statistics
    photobooth_count = Photo.query.filter_by(is_photobooth=True).count()
    
    # Count recent photobooth photos (last 7 days)
    from datetime import datetime, timedelta
    week_ago = datetime.now() - timedelta(days=7)
    recent_photobooth = Photo.query.filter(
        Photo.is_photobooth == True,
        Photo.upload_date >= week_ago
    ).count()
    
    return render_template('admin_photobooth.html',
                         border_settings=border_settings,
                         photobooth_count=photobooth_count,
                         recent_photobooth=recent_photobooth)

@admin_bp.route('/qr-settings')
def admin_qr_settings():
    # Check for SSO session first
    sso_user_email = session.get('sso_user_email')
    sso_user_domain = session.get('sso_user_domain')
    admin_key = request.args.get('key', '')
    
    # Verify admin access
    if not verify_admin_access(admin_key, sso_user_email, sso_user_domain):
        return "Unauthorized", 401
    
    # Get QR settings as JSON object
    qr_settings = Settings.get('qr_settings', '{}')
    qr_settings = json.loads(qr_settings) if qr_settings else {}
    
    # Default values if not set
    if not qr_settings:
        qr_settings = {
            'enabled': True,
            'size': 'medium',
            'color': 'black',
            'custom_text': '',
            'title': 'Scan to View Our Wedding Gallery',
            'subtitle': 'Share your photos and memories with us',
            'message': 'Thank you for celebrating with us!',
            'couple_names': ''
        }
    
    # Generate QR code URL
    qr_code_url = url_for('admin.qr_preview', key=admin_key, color=qr_settings.get('color', 'black'))
    
    return render_template('admin_qr_settings.html',
                         qr_settings=qr_settings,
                         qr_code_url=qr_code_url)

@admin_bp.route('/photo-of-day')
def admin_photo_of_day():
    # Check for SSO session first
    sso_user_email = session.get('sso_user_email')
    sso_user_domain = session.get('sso_user_domain')
    admin_key = request.args.get('key', '')
    
    # Verify admin access
    if not verify_admin_access(admin_key, sso_user_email, sso_user_domain):
        return "Unauthorized", 401
    
    # Import photo of day models
    from app.models.photo_of_day import PhotoOfDay, PhotoOfDayCandidate, PhotoOfDayVote
    from app.models.photo import Photo
    from datetime import datetime, timedelta
    
    # Get all photos of the day
    photos_of_day = PhotoOfDay.query.order_by(PhotoOfDay.date.desc()).all()
    
    # Get candidate photos (photos that could be selected)
    candidate_photos = PhotoOfDayCandidate.query.order_by(PhotoOfDayCandidate.date_added.desc()).all()
    
    # Get all photos for selection
    all_photos = Photo.query.order_by(Photo.upload_date.desc()).limit(100).all()
    
    # Get current settings
    likes_threshold = int(Settings.get('photo_of_day_likes_threshold', '3'))
    
    # Get photos that would be auto-candidates based on current threshold
    auto_candidate_photos = Photo.query.filter(
        Photo.likes >= likes_threshold
    ).order_by(Photo.likes.desc()).limit(20).all()
    
    return render_template('admin_photo_of_day.html',
                         photos_of_day=photos_of_day,
                         candidate_photos=candidate_photos,
                         all_photos=all_photos,
                         likes_threshold=likes_threshold,
                         auto_candidate_photos=auto_candidate_photos)

@admin_bp.route('/welcome-modal')
def admin_welcome_modal():
    # Check for SSO session first
    sso_user_email = session.get('sso_user_email')
    sso_user_domain = session.get('sso_user_domain')
    admin_key = request.args.get('key', '')
    
    # Verify admin access
    if not verify_admin_access(admin_key, sso_user_email, sso_user_domain):
        return "Unauthorized", 401
    
    # Get welcome modal settings as JSON object
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
            'show_once': True,
            'button_text': 'Get Started',
            'background_color': '#8b7355',
            'text_color': '#ffffff',
            'show_on_every_visit': False
        }
    
    return render_template('admin_welcome_modal.html',
                         welcome_settings=welcome_settings)

@admin_bp.route('/sso-settings')
def admin_sso_settings():
    # Check for SSO session first
    sso_user_email = session.get('sso_user_email')
    sso_user_domain = session.get('sso_user_domain')
    admin_key = request.args.get('key', '')
    
    # Verify admin access
    if not verify_admin_access(admin_key, sso_user_email, sso_user_domain):
        return "Unauthorized", 401
    
    # Get SSO settings
    sso_settings = get_sso_settings()
    
    return render_template('admin_sso_settings.html',
                         sso_settings=sso_settings)

@admin_bp.route('/captcha-settings')
def admin_captcha_settings():
    # Check for SSO session first
    sso_user_email = session.get('sso_user_email')
    sso_user_domain = session.get('sso_user_domain')
    admin_key = request.args.get('key', '')
    
    # Verify admin access
    if not verify_admin_access(admin_key, sso_user_email, sso_user_domain):
        return "Unauthorized", 401
    
    # Get CAPTCHA settings
    captcha_settings = {
        'enabled': Settings.get('captcha_enabled', 'true').lower() == 'true',
        'difficulty': Settings.get('captcha_difficulty', 'medium'),
        'timeout': int(Settings.get('captcha_timeout', '10')),
        'max_attempts': int(Settings.get('captcha_max_attempts', '3')),
        'block_duration': int(Settings.get('captcha_block_duration', '15')),
        'guestbook_enabled': Settings.get('captcha_guestbook_enabled', 'true').lower() == 'true',
        'messages_enabled': Settings.get('captcha_messages_enabled', 'true').lower() == 'true',
        'uploads_enabled': Settings.get('captcha_uploads_enabled', 'false').lower() == 'true'
    }
    
    # Get CAPTCHA statistics (you'll need to implement this based on your logging)
    captcha_stats = {
        'total_attempts': 0,
        'successful_attempts': 0,
        'failed_attempts': 0,
        'blocked_ips': 0,
        'success_rate': 0.0,
        'recent_attempts': 0
    }
    
    # Get CAPTCHA logs (you'll need to implement this based on your logging)
    captcha_logs = []
    
    return render_template('admin_captcha_settings.html',
                         captcha_settings=captcha_settings,
                         captcha_stats=captcha_stats,
                         captcha_logs=captcha_logs)

@admin_bp.route('/batch-download')
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
                    file_path = os.path.join(current_app.config['VIDEO_FOLDER'], photo.filename)
                elif photo.is_photobooth:
                    file_path = os.path.join(current_app.config['PHOTOBOOTH_FOLDER'], photo.filename)
                else:
                    file_path = os.path.join(current_app.config['UPLOAD_FOLDER'], photo.filename)
                
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
                    thumb_path = os.path.join(current_app.config['THUMBNAIL_FOLDER'], photo.thumbnail_filename)
                    if os.path.exists(thumb_path):
                        zipf.write(thumb_path, f"video_thumbnails/{photo.thumbnail_filename}")
            
            # Add guestbook photos
            guestbook_entries = GuestbookEntry.query.all()
            for entry in guestbook_entries:
                if entry.photo_filename:
                    file_path = os.path.join(current_app.config['GUESTBOOK_UPLOAD_FOLDER'], entry.photo_filename)
                    if os.path.exists(file_path):
                        zipf.write(file_path, f"guestbook_photos/{entry.photo_filename}")
            
            # Add message board photos
            messages = Message.query.all()
            for message in messages:
                if message.photo_filename:
                    file_path = os.path.join(current_app.config['MESSAGE_UPLOAD_FOLDER'], message.photo_filename)
                    if os.path.exists(file_path):
                        zipf.write(file_path, f"message_photos/{message.photo_filename}")
            
            # Add border files
            border_settings = Settings.get('photobooth_border', '{}')
            border_settings = json.loads(border_settings) if border_settings else {}
            if border_settings.get('filename'):
                border_path = os.path.join(current_app.config['BORDER_FOLDER'], border_settings['filename'])
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

@admin_bp.route('/system-reset', methods=['POST'])
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
            current_app.config['UPLOAD_FOLDER'],
            current_app.config['VIDEO_FOLDER'],
            current_app.config['THUMBNAIL_FOLDER'],
            current_app.config['PHOTOBOOTH_FOLDER'],
            current_app.config['GUESTBOOK_UPLOAD_FOLDER'],
            current_app.config['MESSAGE_UPLOAD_FOLDER'],
            current_app.config['BORDER_FOLDER']
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

@admin_bp.route('/upload-border', methods=['POST'])
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
    
    from app.utils.file_utils import allowed_file
    if file and allowed_file(file.filename):
        # Remove old border file if exists
        border_settings = Settings.get('photobooth_border', '{}')
        border_settings = json.loads(border_settings) if border_settings else {}
        
        if border_settings.get('filename'):
            old_filepath = os.path.join(current_app.config['BORDER_FOLDER'], border_settings['filename'])
            if os.path.exists(old_filepath):
                os.remove(old_filepath)
        
        # Save new border
        filename = secure_filename(file.filename)
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        filename = f"border_{timestamp}_{filename}"
        filepath = os.path.join(current_app.config['BORDER_FOLDER'], filename)
        
        # Ensure border folder exists
        os.makedirs(current_app.config['BORDER_FOLDER'], exist_ok=True)
        
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

@admin_bp.route('/remove-border', methods=['POST'])
def remove_border():
    # Check for SSO session first
    sso_user_email = session.get('sso_user_email')
    sso_user_domain = session.get('sso_user_domain')
    admin_key = request.args.get('key', '')
    
    # Verify admin access
    if not verify_admin_access(admin_key, sso_user_email, sso_user_domain):
        return "Unauthorized", 401
    
    try:
        # Get current border settings
        border_settings = Settings.get('photobooth_border', '{}')
        border_settings = json.loads(border_settings) if border_settings else {}
        
        # Remove file if exists
        if border_settings.get('filename'):
            filepath = os.path.join(current_app.config['BORDER_FOLDER'], border_settings['filename'])
            if os.path.exists(filepath):
                os.remove(filepath)
            
            # Clear settings
            Settings.set('photobooth_border', '{}')
        
        return jsonify({'success': True, 'message': 'Border removed successfully'})
    except Exception as e:
        return jsonify({'error': f'Error removing border: {str(e)}'}), 500

@admin_bp.route('/upload-couple-photo', methods=['POST'])
def upload_couple_photo():
    # Check for SSO session first
    sso_user_email = session.get('sso_user_email')
    sso_user_domain = session.get('sso_user_domain')
    admin_key = request.args.get('key', '')
    
    # Verify admin access
    if not verify_admin_access(admin_key, sso_user_email, sso_user_domain):
        return "Unauthorized", 401
    
    if 'couple_photo' not in request.files:
        return jsonify({'error': 'No file provided'}), 400
    
    file = request.files['couple_photo']
    if file.filename == '':
        return jsonify({'error': 'No file selected'}), 400
    
    from app.utils.file_utils import allowed_file
    if file and allowed_file(file.filename):
        # Remove old couple photo if exists
        welcome_settings = Settings.get('welcome_modal', '{}')
        welcome_settings = json.loads(welcome_settings) if welcome_settings else {}
        
        if welcome_settings.get('couple_photo'):
            old_filepath = os.path.join(current_app.config['UPLOAD_FOLDER'], welcome_settings['couple_photo'])
            if os.path.exists(old_filepath):
                os.remove(old_filepath)
        
        # Save new couple photo
        filename = secure_filename(file.filename)
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        filename = f"couple_photo_{timestamp}_{filename}"
        filepath = os.path.join(current_app.config['UPLOAD_FOLDER'], filename)
        
        # Ensure upload folder exists
        os.makedirs(current_app.config['UPLOAD_FOLDER'], exist_ok=True)
        
        file.save(filepath)
        
        # Update settings
        welcome_settings['couple_photo'] = filename
        Settings.set('welcome_modal', json.dumps(welcome_settings))
        
        return jsonify({'success': True, 'message': 'Couple photo uploaded successfully'})
    else:
        return jsonify({'error': 'Invalid file type'}), 400

@admin_bp.route('/remove-couple-photo', methods=['POST'])
def remove_couple_photo():
    # Check for SSO session first
    sso_user_email = session.get('sso_user_email')
    sso_user_domain = session.get('sso_user_domain')
    admin_key = request.args.get('key', '')
    
    # Verify admin access
    if not verify_admin_access(admin_key, sso_user_email, sso_user_domain):
        return "Unauthorized", 401
    
    try:
        # Get current welcome settings
        welcome_settings = Settings.get('welcome_modal', '{}')
        welcome_settings = json.loads(welcome_settings) if welcome_settings else {}
        
        # Remove file if exists
        if welcome_settings.get('couple_photo'):
            filepath = os.path.join(current_app.config['UPLOAD_FOLDER'], welcome_settings['couple_photo'])
            if os.path.exists(filepath):
                os.remove(filepath)
            
            # Remove from settings
            del welcome_settings['couple_photo']
            Settings.set('welcome_modal', json.dumps(welcome_settings))
        
        return jsonify({'success': True, 'message': 'Couple photo removed successfully'})
    except Exception as e:
        return jsonify({'error': f'Error removing couple photo: {str(e)}'}), 500

@admin_bp.route('/delete/<int:photo_id>')
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
            os.remove(os.path.join(current_app.config['VIDEO_FOLDER'], photo.filename))
            if photo.thumbnail_filename:
                os.remove(os.path.join(current_app.config['THUMBNAIL_FOLDER'], photo.thumbnail_filename))
        elif photo.is_photobooth:
            os.remove(os.path.join(current_app.config['PHOTOBOOTH_FOLDER'], photo.filename))
        else:
            os.remove(os.path.join(current_app.config['UPLOAD_FOLDER'], photo.filename))
    except:
        pass
    
    # Delete from database
    db.session.delete(photo)
    db.session.commit()
    
    return redirect(url_for('admin.admin'))

@admin_bp.route('/delete-guestbook/<int:entry_id>')
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
            os.remove(os.path.join(current_app.config['GUESTBOOK_UPLOAD_FOLDER'], entry.photo_filename))
        except:
            pass
    
    db.session.delete(entry)
    db.session.commit()
    
    return redirect(url_for('admin.admin'))

@admin_bp.route('/toggle-message/<int:message_id>')
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
    
    return redirect(url_for('admin.admin'))

@admin_bp.route('/delete-message/<int:message_id>')
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
            os.remove(os.path.join(current_app.config['MESSAGE_UPLOAD_FOLDER'], message.photo_filename))
        except:
            pass
    
    db.session.delete(message)
    db.session.commit()
    
    return redirect(url_for('admin.admin'))

@admin_bp.route('/toggle-message-comment/<int:comment_id>')
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
    
    return redirect(url_for('admin.admin'))

@admin_bp.route('/delete-message-comment/<int:comment_id>')
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
    
    return redirect(url_for('admin.admin'))

@admin_bp.route('/edit-guestbook/<int:entry_id>', methods=['POST'])
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

@admin_bp.route('/save-settings', methods=['POST'])
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
    
    # Save CAPTCHA settings
    if 'captcha_settings' in data:
        captcha_data = data['captcha_settings']
        Settings.set('captcha_enabled', str(captcha_data.get('enabled', False)).lower())
        Settings.set('captcha_upload_enabled', str(captcha_data.get('upload_enabled', True)).lower())
        Settings.set('captcha_guestbook_enabled', str(captcha_data.get('guestbook_enabled', True)).lower())
        Settings.set('captcha_message_enabled', str(captcha_data.get('message_enabled', True)).lower())
    
    # Save timezone settings
    if 'timezone_settings' in data:
        timezone_data = data['timezone_settings']
        Settings.set('timezone_settings', json.dumps(timezone_data))
    
    # Save slideshow settings
    if 'slideshow_settings' in data:
        slideshow_data = data['slideshow_settings']
        
        # Import slideshow settings model
        from app.models.slideshow import SlideshowSettings
        
        # Save all slideshow settings to the slideshow_settings table
        slideshow_settings_mapping = {
            'enabled': slideshow_data.get('enabled', True),
            'speed': slideshow_data.get('speed', 3),
            'effect': slideshow_data.get('effect', 'fade'),
            'order': slideshow_data.get('order', 'random'),
            'max_photos': slideshow_data.get('max_photos', 20),
            'autoplay': slideshow_data.get('autoplay', True),
            'loop': slideshow_data.get('loop', True),
            'show_controls': slideshow_data.get('show_controls', True),
            'slideshow_interval': slideshow_data.get('slideshow_interval', 5000),
            'show_photos': slideshow_data.get('show_photos', True),
            'show_guestbook': slideshow_data.get('show_guestbook', True),
            'show_messages': slideshow_data.get('show_messages', True),
            'time_range_hours': slideshow_data.get('time_range_hours', 24),
            'max_activities': slideshow_data.get('max_activities', 50)
        }
        
        for key, value in slideshow_settings_mapping.items():
            setting = SlideshowSettings.query.filter_by(key=key).first()
            if setting:
                setting.value = str(value)
            else:
                setting = SlideshowSettings(key=key, value=str(value))
                db.session.add(setting)
        
        db.session.commit()
    
    return jsonify({'success': True})

@admin_bp.route('/start-email-monitor', methods=['POST'])
def start_email_monitor_route():
    # Check for SSO session first
    sso_user_email = session.get('sso_user_email')
    sso_user_domain = session.get('sso_user_domain')
    admin_key = request.args.get('key', '')
    
    # Verify admin access
    if not verify_admin_access(admin_key, sso_user_email, sso_user_domain):
        return "Unauthorized", 401
    
    try:
        start_email_monitor()
        return jsonify({'success': True, 'message': 'Email monitor started successfully'})
    except Exception as e:
        return jsonify({'success': False, 'message': f'Error starting email monitor: {str(e)}'})

@admin_bp.route('/sync-immich', methods=['POST'])
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

@admin_bp.route('/notification-users')
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

@admin_bp.route('/send-notification', methods=['POST'])
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

@admin_bp.route('/generate-qr-pdf')
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
    
    # Get email settings
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
    
    # Create PDF with smaller margins to fit everything
    pdf_buffer = BytesIO()
    doc = SimpleDocTemplate(pdf_buffer, pagesize=letter, topMargin=0.5*inch, bottomMargin=0.5*inch, leftMargin=0.5*inch, rightMargin=0.5*inch)
    
    # Styles
    styles = getSampleStyleSheet()
    
    # Custom styles
    title_style = ParagraphStyle(
        'CustomTitle',
        parent=styles['Heading1'],
        fontSize=24,
        textColor=colors.HexColor('#8b7355'),
        spaceAfter=6,
        alignment=TA_CENTER,
        fontName='Helvetica-Bold'
    )
    
    subtitle_style = ParagraphStyle(
        'CustomSubtitle',
        parent=styles['Heading2'],
        fontSize=14,
        textColor=colors.HexColor('#6b5d54'),
        spaceAfter=12,
        alignment=TA_CENTER,
        fontName='Helvetica'
    )
    
    body_style = ParagraphStyle(
        'CustomBody',
        parent=styles['BodyText'],
        fontSize=10,
        textColor=colors.HexColor('#444444'),
        alignment=TA_CENTER,
        spaceAfter=8,
        leading=12
    )
    
    feature_style = ParagraphStyle(
        'FeatureStyle',
        parent=styles['BodyText'],
        fontSize=9,
        textColor=colors.HexColor('#666666'),
        alignment=TA_LEFT,
        spaceAfter=4,
        leading=11,
        leftIndent=10
    )
    
    email_style = ParagraphStyle(
        'EmailStyle',
        parent=styles['BodyText'],
        fontSize=10,
        textColor=colors.HexColor('#8b7355'),
        alignment=TA_CENTER,
        spaceAfter=8,
        leading=12,
        fontName='Helvetica-Bold'
    )
    
    couple_style = ParagraphStyle(
        'CoupleNames',
        parent=styles['BodyText'],
        fontSize=12,
        textColor=colors.HexColor('#8b7355'),
        alignment=TA_CENTER,
        fontName='Helvetica-Oblique'
    )
    
    url_style = ParagraphStyle(
        'URLStyle',
        parent=styles['BodyText'],
        fontSize=8,
        textColor=colors.HexColor('#666666'),
        alignment=TA_CENTER,
        spaceAfter=8
    )
    
    # Build PDF content
    story = []
    
    # Decorative header
    header_decoration = Table([['💒 💕 💒']], colWidths=[7*inch])
    header_decoration.setStyle(TableStyle([
        ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
        ('FONTNAME', (0, 0), (-1, -1), 'Helvetica'),
        ('FONTSIZE', (0, 0), (-1, -1), 18),
        ('TEXTCOLOR', (0, 0), (-1, -1), colors.HexColor('#8b7355')),
    ]))
    story.append(header_decoration)
    story.append(Spacer(1, 0.1*inch))
    
    # Title
    story.append(Paragraph(title, title_style))
    story.append(Paragraph(subtitle, subtitle_style))
    
    # Main message
    story.append(Paragraph(message, body_style))
    story.append(Spacer(1, 0.1*inch))
    
    # Email upload section
    email_section = f"""
    <b>📧 Email Your Photos Directly!</b><br/>
    Send photos to: <b>{monitor_email}</b><br/>
    <i>Supports: JPG, PNG, GIF, WebP</i>
    """
    story.append(Paragraph(email_section, email_style))
    story.append(Spacer(1, 0.15*inch))
    
    # QR Code (smaller to fit more content)
    qr_image = Image(qr_buffer, width=2*inch, height=2*inch)
    qr_image.hAlign = 'CENTER'
    story.append(qr_image)
    story.append(Spacer(1, 0.1*inch))
    
    # URL
    story.append(Paragraph(f"<i>{public_url}</i>", url_style))
    story.append(Spacer(1, 0.1*inch))
    
    # Features section
    features_title = Paragraph("<b>🎉 What You Can Do:</b>", body_style)
    story.append(features_title)
    story.append(Spacer(1, 0.05*inch))
    
    # Features list
    features = [
        "📸 Upload photos and videos from your phone",
        "💬 Leave messages and comments on photos",
        "📝 Sign our digital guestbook with photos",
        "🎭 Try our virtual photobooth with fun borders",
        "👀 Browse the complete wedding gallery",
        "❤️ Like and react to your favorite photos",
        "📱 Works great on phones and tablets",
        "🔔 Get notifications when new photos are added"
    ]
    
    for feature in features:
        story.append(Paragraph(f"• {feature}", feature_style))
    
    story.append(Spacer(1, 0.1*inch))
    
    # Instructions
    instructions = """
    <b>How to Use:</b><br/>
    1. Scan the QR code above with your phone camera<br/>
    2. Or visit the website directly<br/>
    3. Upload photos, leave messages, and enjoy!<br/>
    4. No login required - just add your name when uploading
    """
    story.append(Paragraph(instructions, body_style))
    story.append(Spacer(1, 0.1*inch))
    
    # Couple names
    story.append(Paragraph(f"With love,<br/>{couple_names}", couple_style))
    
    # Decorative footer
    footer_decoration = Table([['💕 Thank You for Celebrating With Us! 💕']], colWidths=[7*inch])
    footer_decoration.setStyle(TableStyle([
        ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
        ('FONTNAME', (0, 0), (-1, -1), 'Helvetica'),
        ('FONTSIZE', (0, 0), (-1, -1), 10),
        ('TEXTCOLOR', (0, 0), (-1, -1), colors.HexColor('#8b7355')),
    ]))
    story.append(Spacer(1, 0.1*inch))
    story.append(footer_decoration)
    
    # Build PDF
    doc.build(story)
    
    pdf_buffer.seek(0)
    
    return send_file(
        pdf_buffer,
        mimetype='application/pdf',
        as_attachment=True,
        download_name='wedding_photo_invitation.pdf'
    )

@admin_bp.route('/pwa-debug')
def pwa_debug():
    # Check for SSO session first
    sso_user_email = session.get('sso_user_email')
    sso_user_domain = session.get('sso_user_domain')
    admin_key = request.args.get('key', '')
    
    # Verify admin access
    if not verify_admin_access(admin_key, sso_user_email, sso_user_domain):
        return "Unauthorized", 401
    
    return render_template('pwa_debug.html')

@admin_bp.route('/debug/push-notification-test')
def debug_push_notification_test():
    """Debug endpoint for testing push notifications"""
    try:
        # Create a test notification for the current user
        user_identifier = request.cookies.get('user_identifier', 'test-user')
        
        # Create a test notification
        from app.utils.notification_utils import create_notification_with_push
        
        success = create_notification_with_push(
            user_identifier=user_identifier,
            title='🧪 Test Notification',
            message='This is a test push notification from the debug panel!',
            notification_type='admin',
            content_type='debug',
            content_id=0
        )
        
        if success:
            return jsonify({
                'success': True,
                'message': 'Test notification created successfully',
                'user_identifier': user_identifier
            })
        else:
            return jsonify({
                'success': False,
                'message': 'Failed to create test notification'
            })
            
    except Exception as e:
        print(f"Error in debug push notification test: {e}")
        return jsonify({
            'success': False,
            'message': f'Error: {str(e)}'
        })

@admin_bp.route('/debug/notification-users')
def debug_notification_users():
    """Debug endpoint for viewing notification users"""
    try:
        from app.models.notifications import NotificationUser, Notification
        
        # Get all notification users with their unread count
        users = NotificationUser.query.all()
        user_data = []
        
        for user in users:
            unread_count = Notification.query.filter_by(
                user_identifier=user.user_identifier,
                is_read=False
            ).count()
            
            user_data.append({
                'user_name': user.user_name,
                'user_identifier': user.user_identifier,
                'notifications_enabled': user.notifications_enabled,
                'push_enabled': user.push_enabled,
                'push_permission_granted': user.push_permission_granted,
                'unread_count': unread_count,
                'last_seen': user.last_seen.isoformat() if user.last_seen else None,
                'created_at': user.created_at.isoformat() if user.created_at else None
            })
        
        return jsonify({
            'success': True,
            'users': user_data
        })
        
    except Exception as e:
        print(f"Error in debug notification users: {e}")
        return jsonify({
            'success': False,
            'message': f'Error: {str(e)}'
        })

@admin_bp.route('/register-notification-user', methods=['POST'])
def register_notification_user():
    # Check for SSO session first
    sso_user_email = session.get('sso_user_email')
    sso_user_domain = session.get('sso_user_domain')
    admin_key = request.args.get('key', '')
    
    # Verify admin access
    if not verify_admin_access(admin_key, sso_user_email, sso_user_domain):
        return jsonify({'success': False, 'message': 'Unauthorized'}), 401
    
    try:
        data = request.get_json()
        user_identifier = data.get('user_identifier', '')
        user_name = data.get('user_name', 'Anonymous')
        device_info = data.get('device_info', '')
        
        if not user_identifier:
            return jsonify({'success': False, 'message': 'User identifier required'})
        
        # Find or create user
        user = NotificationUser.query.filter_by(user_identifier=user_identifier).first()
        if user:
            # Update existing user
            user.user_name = user_name
            user.device_info = device_info
            user.last_seen = datetime.utcnow()
        else:
            # Create new user
            user = NotificationUser(
                user_identifier=user_identifier,
                user_name=user_name,
                device_info=device_info
            )
            db.session.add(user)
        
        db.session.commit()
        return jsonify({'success': True, 'message': 'User registered successfully'})
    
    except Exception as e:
        print(f"Error registering notification user: {e}")
        db.session.rollback()
        return jsonify({'success': False, 'message': str(e)}) 

@admin_bp.route('/database-maintenance', methods=['POST'])
def database_maintenance():
    """Run database maintenance tasks"""
    # Check for SSO session first
    sso_user_email = session.get('sso_user_email')
    sso_user_domain = session.get('sso_user_domain')
    admin_key = request.args.get('key', '')
    
    # Verify admin access
    if not verify_admin_access(admin_key, sso_user_email, sso_user_domain):
        return "Unauthorized", 401
    
    try:
        # Run maintenance task
        success = maintenance_task()
        
        if success:
            return jsonify({
                'success': True,
                'message': 'Database maintenance completed successfully'
            })
        else:
            return jsonify({
                'success': False,
                'error': 'Database maintenance failed'
            }), 500
            
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500

@admin_bp.route('/database-optimize', methods=['POST'])
def database_optimize():
    """Optimize database queries and indexes"""
    # Check for SSO session first
    sso_user_email = session.get('sso_user_email')
    sso_user_domain = session.get('sso_user_domain')
    admin_key = request.args.get('key', '')
    
    # Verify admin access
    if not verify_admin_access(admin_key, sso_user_email, sso_user_domain):
        return "Unauthorized", 401
    
    try:
        # Run database optimization
        success = db_optimizer.optimize_queries()
        
        if success:
            return jsonify({
                'success': True,
                'message': 'Database optimization completed successfully'
            })
        else:
            return jsonify({
                'success': False,
                'error': 'Database optimization failed'
            }), 500
            
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500

@admin_bp.route('/clear-cache', methods=['POST'])
def clear_cache():
    """Clear query cache"""
    # Check for SSO session first
    sso_user_email = session.get('sso_user_email')
    sso_user_domain = session.get('sso_user_domain')
    admin_key = request.args.get('key', '')
    
    # Verify admin access
    if not verify_admin_access(admin_key, sso_user_email, sso_user_domain):
        return "Unauthorized", 401
    
    try:
        # Clear cache
        db_optimizer.clear_cache()
        
        return jsonify({
            'success': True,
            'message': 'Cache cleared successfully'
        })
        
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500 

@admin_bp.route('/slideshow')
def admin_slideshow():
    # Check for SSO session first
    sso_user_email = session.get('sso_user_email')
    sso_user_domain = session.get('sso_user_domain')
    admin_key = request.args.get('key', '')
    
    # Verify admin access
    if not verify_admin_access(admin_key, sso_user_email, sso_user_domain):
        # If SSO is enabled, redirect to SSO login
        sso_settings = get_sso_settings()
        if sso_settings['enabled']:
            return redirect(url_for('auth.sso_login'))
        else:
            return "Unauthorized", 401
    
    # Get slideshow settings
    from app.views.slideshow import get_slideshow_settings
    slideshow_settings = get_slideshow_settings()
    
    # Get recent activities for slideshow
    from datetime import datetime, timedelta
    from app.models.photo import Photo
    from app.models.guestbook import GuestbookEntry
    from app.models.messages import Message
    
    # Get recent photos (last 24 hours)
    since_time = datetime.utcnow() - timedelta(hours=24)
    recent_photos = Photo.query.filter(
        Photo.upload_date >= since_time
    ).order_by(Photo.upload_date.desc()).limit(20).all()
    
    # Get recent guestbook entries
    recent_guestbook = GuestbookEntry.query.filter(
        GuestbookEntry.created_at >= since_time
    ).order_by(GuestbookEntry.created_at.desc()).limit(10).all()
    
    # Get recent messages
    recent_messages = Message.query.filter(
        Message.created_at >= since_time,
        Message.is_hidden == False
    ).order_by(Message.created_at.desc()).limit(10).all()
    
    return render_template('admin_slideshow.html',
                         slideshow_settings=slideshow_settings,
                         recent_photos=recent_photos,
                         recent_guestbook=recent_guestbook,
                         recent_messages=recent_messages,
                         admin_key=admin_key)

@admin_bp.route('/logs')
def admin_logs():
    # Check for SSO session first
    sso_user_email = session.get('sso_user_email')
    sso_user_domain = session.get('sso_user_domain')
    admin_key = request.args.get('key', '')
    
    # Verify admin access
    if not verify_admin_access(admin_key, sso_user_email, sso_user_domain):
        # If SSO is enabled, redirect to SSO login
        sso_settings = get_sso_settings()
        if sso_settings['enabled']:
            return redirect(url_for('auth.sso_login'))
        else:
            return "Unauthorized", 401
    
    # Get email logs
    email_logs = EmailLog.query.order_by(EmailLog.received_at.desc()).limit(100).all()
    
    # Get Immich sync logs
    immich_sync_logs = ImmichSyncLog.query.order_by(ImmichSyncLog.sync_date.desc()).limit(100).all()
    
    # Get system logs
    from app.models.email import SystemLog
    system_logs = SystemLog.query.order_by(SystemLog.timestamp.desc()).limit(100).all()
    
    # Log access to admin logs page
    log_info('system', 'Admin logs page accessed', user_identifier=request.cookies.get('user_identifier', ''))
    
    # Log counts for debugging
    log_info('system', f'Log counts - Email: {len(email_logs)}, Immich: {len(immich_sync_logs)}, System: {len(system_logs)}')
    
    return render_template('admin_logs.html',
                         email_logs=email_logs,
                         immich_sync_logs=immich_sync_logs,
                         system_logs=system_logs,
                         admin_key=admin_key)

@admin_bp.route('/database')
def admin_database():
    # Check for SSO session first
    sso_user_email = session.get('sso_user_email')
    sso_user_domain = session.get('sso_user_domain')
    admin_key = request.args.get('key', '')
    
    # Verify admin access
    if not verify_admin_access(admin_key, sso_user_email, sso_user_domain):
        # If SSO is enabled, redirect to SSO login
        sso_settings = get_sso_settings()
        if sso_settings['enabled']:
            return redirect(url_for('auth.sso_login'))
        else:
            return "Unauthorized", 401
    
    # Get database statistics
    from app.models.photo import Photo
    from app.models.guestbook import GuestbookEntry
    from app.models.messages import Message, MessageComment
    from app.models.notifications import NotificationUser, Notification
    
    stats = {
        'total_photos': Photo.query.count(),
        'total_guestbook': GuestbookEntry.query.count(),
        'total_messages': Message.query.count(),
        'total_comments': MessageComment.query.count(),
        'total_notification_users': NotificationUser.query.count(),
        'total_notifications': Notification.query.count(),
        'total_email_logs': EmailLog.query.count(),
        'total_immich_logs': ImmichSyncLog.query.count()
    }
    
    # Get database optimization status
    from app.utils.db_optimization import db_optimizer
    cache_size = db_optimizer.get_cache_size()
    optimization_status = {
        'cache_enabled': db_optimizer.is_enabled(),
        'cache_size': f"{cache_size} MB" if cache_size > 0 else "0 MB",
        'last_optimization': Settings.get('last_database_optimization', 'Never'),
        'database_size': 'Unknown'  # Could be implemented to get actual DB size
    }
    
    return render_template('admin_database.html',
                         stats=stats,
                         optimization_status=optimization_status,
                         admin_key=admin_key) 

@admin_bp.route('/qr-preview')
def qr_preview():
    # Check for SSO session first
    sso_user_email = session.get('sso_user_email')
    sso_user_domain = session.get('sso_user_domain')
    admin_key = request.args.get('key', '')
    
    # Verify admin access
    if not verify_admin_access(admin_key, sso_user_email, sso_user_domain):
        return "Unauthorized", 401
    
    # Get QR settings
    qr_settings = Settings.get('qr_settings', '{}')
    qr_settings = json.loads(qr_settings) if qr_settings else {}
    
    # Get parameters
    color = request.args.get('color', qr_settings.get('color', 'black'))
    size = qr_settings.get('size', 'medium')
    
    # Generate QR code URL
    base_url = request.host_url.rstrip('/')
    qr_data = f"{base_url}/?key={admin_key}"
    
    # Generate QR code
    import qrcode
    from io import BytesIO
    from PIL import Image
    
    # Create QR code
    qr = qrcode.QRCode(
        version=1,
        error_correction=qrcode.constants.ERROR_CORRECT_L,
        box_size=10,
        border=4,
    )
    qr.add_data(qr_data)
    qr.make(fit=True)
    
    # Create QR code image
    qr_image = qr.make_image(fill_color=color, back_color="white")
    
    # Resize based on size setting
    size_map = {
        'small': 200,
        'medium': 300,
        'large': 400
    }
    target_size = size_map.get(size, 300)
    qr_image = qr_image.resize((target_size, target_size), Image.Resampling.LANCZOS)
    
    # Convert to bytes
    img_io = BytesIO()
    qr_image.save(img_io, 'PNG')
    img_io.seek(0)
    
    from flask import send_file
    return send_file(img_io, mimetype='image/png')

@admin_bp.route('/download-qr')
def download_qr():
    # Check for SSO session first
    sso_user_email = session.get('sso_user_email')
    sso_user_domain = session.get('sso_user_domain')
    admin_key = request.args.get('key', '')
    
    # Verify admin access
    if not verify_admin_access(admin_key, sso_user_email, sso_user_domain):
        return "Unauthorized", 401
    
    # Get QR settings
    qr_settings = Settings.get('qr_settings', '{}')
    qr_settings = json.loads(qr_settings) if qr_settings else {}
    
    # Get parameters
    color = request.args.get('color', qr_settings.get('color', 'black'))
    format_type = request.args.get('format', 'png')
    size = qr_settings.get('size', 'medium')
    
    # Generate QR code URL
    base_url = request.host_url.rstrip('/')
    qr_data = f"{base_url}/?key={admin_key}"
    
    # Generate QR code
    import qrcode
    from io import BytesIO
    from PIL import Image
    
    # Create QR code
    qr = qrcode.QRCode(
        version=1,
        error_correction=qrcode.constants.ERROR_CORRECT_L,
        box_size=10,
        border=4,
    )
    qr.add_data(qr_data)
    qr.make(fit=True)
    
    # Create QR code image
    qr_image = qr.make_image(fill_color=color, back_color="white")
    
    # Resize based on size setting
    size_map = {
        'small': 200,
        'medium': 300,
        'large': 400
    }
    target_size = size_map.get(size, 300)
    qr_image = qr_image.resize((target_size, target_size), Image.Resampling.LANCZOS)
    
    # Convert to bytes
    img_io = BytesIO()
    
    if format_type == 'svg':
        # For SVG, we'll create a simple SVG representation
        svg_content = f'''<?xml version="1.0" encoding="UTF-8"?>
<svg width="{target_size}" height="{target_size}" xmlns="http://www.w3.org/2000/svg">
    <rect width="100%" height="100%" fill="white"/>
    <text x="50%" y="50%" text-anchor="middle" dy=".3em" font-family="Arial" font-size="12" fill="{color}">
        QR Code - Wedding Gallery
    </text>
</svg>'''
        img_io.write(svg_content.encode())
        mimetype = 'image/svg+xml'
        filename = 'wedding-qr-code.svg'
    else:
        # PNG format
        qr_image.save(img_io, 'PNG')
        mimetype = 'image/png'
        filename = 'wedding-qr-code.png'
    
    img_io.seek(0)
    
    from flask import send_file
    return send_file(
        img_io, 
        mimetype=mimetype,
        as_attachment=True,
        download_name=filename
    ) 

@admin_bp.route('/timezone-settings')
def admin_timezone_settings():
    # Check for SSO session first
    sso_user_email = session.get('sso_user_email')
    sso_user_domain = session.get('sso_user_domain')
    admin_key = request.args.get('key', '')
    
    # Verify admin access
    if not verify_admin_access(admin_key, sso_user_email, sso_user_domain):
        return "Unauthorized", 401
    
    # Get timezone settings
    timezone_settings = Settings.get('timezone_settings', '{}')
    timezone_settings = json.loads(timezone_settings) if timezone_settings else {}
    
    # Calculate current time in selected timezone
    from datetime import datetime
    from app.utils.settings_utils import format_datetime_in_timezone
    current_time = format_datetime_in_timezone(datetime.utcnow())
    
    return render_template('admin_timezone_settings.html', 
                         timezone_settings=timezone_settings,
                         current_time=current_time,
                         admin_key=admin_key)