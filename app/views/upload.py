from flask import Blueprint, render_template, request, redirect, url_for, make_response, current_app
from werkzeug.utils import secure_filename
from datetime import datetime
import secrets
import os
from app.models.photo import Photo
from app import db
from app.utils.file_utils import allowed_file, is_video, is_image, get_video_duration, create_video_thumbnail
from app.utils.settings_utils import get_email_settings, get_immich_settings
from app.utils.immich_utils import sync_file_to_immich
from app.utils.captcha_utils import is_captcha_enabled, validate_captcha, generate_captcha, get_captcha_settings
from app.utils.system_logger import log_upload_event, log_error, log_exception

upload_bp = Blueprint('upload', __name__)

@upload_bp.route('/', methods=['GET', 'POST'])
def upload():
    if request.method == 'POST':
        # Check CAPTCHA if enabled
        captcha_settings = get_captcha_settings()
        if captcha_settings['enabled'] and captcha_settings['upload_enabled']:
            challenge_id = request.form.get('captcha_challenge_id')
            user_answer = request.form.get('captcha_answer')
            
            if not validate_captcha(challenge_id, user_answer):
                # Generate new CAPTCHA for retry
                captcha = generate_captcha()
                return render_template('upload.html', 
                                     user_name=request.cookies.get('user_name', ''),
                                     email_settings=get_email_settings(),
                                     captcha=captcha,
                                     error='Incorrect CAPTCHA answer. Please try again.')
        
        if 'photo' not in request.files:
            log_error('upload', 'No file uploaded', user_identifier=request.cookies.get('user_identifier', ''))
            return redirect(request.url)
        
        file = request.files['photo']
        if file.filename == '':
            log_error('upload', 'Empty filename provided', user_identifier=request.cookies.get('user_identifier', ''))
            return redirect(request.url)
        
        if file and allowed_file(file.filename):
            # Log successful upload start
            log_upload_event(f"Upload started: {file.filename}", 
                           user_identifier=user_identifier,
                           details={'filename': file.filename, 'uploader_name': uploader_name})
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
                filepath = os.path.join(current_app.config['VIDEO_FOLDER'], filename)
                file.save(filepath)
                
                # Check video duration
                duration = get_video_duration(filepath)
                if duration and duration > current_app.config['MAX_VIDEO_DURATION']:
                    os.remove(filepath)
                    log_error('upload', f'Video too long: {duration}s > {current_app.config["MAX_VIDEO_DURATION"]}s', 
                             user_identifier=user_identifier,
                             details={'filename': file.filename, 'duration': duration})
                    return render_template('upload.html', 
                                         user_name=request.cookies.get('user_name', ''),
                                         error=f'Video must be {current_app.config["MAX_VIDEO_DURATION"]} seconds or less')
                
                # Create thumbnail
                thumbnail_filename = f"thumb_{timestamp}_{os.path.splitext(filename)[0]}.jpg"
                thumbnail_path = os.path.join(current_app.config['THUMBNAIL_FOLDER'], thumbnail_filename)
                
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
                filepath = os.path.join(current_app.config['UPLOAD_FOLDER'], filename)
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
            
            # Log successful upload
            log_upload_event(f"Upload completed: {photo.filename}", 
                           user_identifier=user_identifier,
                           details={'photo_id': photo.id, 'media_type': photo.media_type, 'file_size': os.path.getsize(filepath)})
            
            # Sync to Immich if enabled
            try:
                immich_settings = get_immich_settings()
                if immich_settings['enabled']:
                    if photo.media_type == 'video' and immich_settings['sync_videos']:
                        file_path = os.path.join(current_app.config['VIDEO_FOLDER'], photo.filename)
                        description = f"Wedding video by {photo.uploader_name}"
                        if photo.description:
                            description += f" - {photo.description}"
                        sync_file_to_immich(file_path, photo.filename, description)
                    elif photo.media_type == 'image' and immich_settings['sync_photos']:
                        file_path = os.path.join(current_app.config['UPLOAD_FOLDER'], photo.filename)
                        description = f"Wedding photo by {photo.uploader_name}"
                        if photo.description:
                            description += f" - {photo.description}"
                        sync_file_to_immich(file_path, photo.filename, description)
            except Exception as e:
                log_exception('immich', f"Error syncing to Immich: {e}", exception=e, user_identifier=user_identifier)
                print(f"Error syncing to Immich: {e}")
            
            # Save user name in cookie
            resp = make_response(redirect(url_for('main.index')))
            resp.set_cookie('user_name', uploader_name, max_age=30*24*60*60)  # 30 days
            resp.set_cookie('user_identifier', user_identifier, max_age=365*24*60*60)  # 1 year
            return resp
    
    # Get or create user identifier for visitors to upload page
    user_identifier = request.cookies.get('user_identifier', '')
    if not user_identifier:
        user_identifier = secrets.token_hex(16)
    
    user_name = request.cookies.get('user_name', '')
    email_settings = get_email_settings()
    captcha_settings = get_captcha_settings()
    
    # Generate CAPTCHA if enabled
    captcha = None
    if captcha_settings['enabled'] and captcha_settings['upload_enabled']:
        captcha = generate_captcha()
    
    # Create response with user identifier cookie if needed
    if not request.cookies.get('user_identifier'):
        resp = make_response(render_template('upload.html', 
                                           user_name=user_name, 
                                           email_settings=email_settings,
                                           captcha=captcha))
        resp.set_cookie('user_identifier', user_identifier, max_age=365*24*60*60)  # 1 year
        return resp
    
    return render_template('upload.html', 
                         user_name=user_name, 
                         email_settings=email_settings,
                         captcha=captcha) 