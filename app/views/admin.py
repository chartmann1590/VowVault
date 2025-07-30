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
from reportlab.lib.enums import TA_CENTER, TA_JUSTIFY
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
    
    # Get saved settings
    public_url = Settings.get('public_url', '')
    qr_settings = Settings.get('qr_settings', '{}')
    qr_settings = json.loads(qr_settings) if qr_settings else {}
    
    welcome_settings = Settings.get('welcome_modal', '{}')
    welcome_settings = json.loads(welcome_settings) if welcome_settings else {}
    
    border_settings = Settings.get('photobooth_border', '{}')
    border_settings = json.loads(border_settings) if border_settings else {}
    
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
                         email_settings=email_settings,
                         email_logs=email_logs,
                         immich_settings=immich_settings,
                         immich_sync_logs=immich_sync_logs,
                         sso_settings=sso_settings,
                         current_user=current_user)

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