from flask import Blueprint, render_template, request, make_response, redirect, url_for, jsonify, current_app
from werkzeug.utils import secure_filename
from datetime import datetime
import secrets
import os
from app.models.messages import Message, MessageComment, MessageLike
from app import db
from app.utils.file_utils import allowed_file
from app.utils.settings_utils import get_immich_settings
from app.utils.immich_utils import sync_file_to_immich
from app.utils.notification_utils import create_notification_with_push
from app.utils.captcha_utils import get_captcha_settings, validate_captcha, generate_captcha

messages_bp = Blueprint('messages', __name__)

@messages_bp.route('/')
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

@messages_bp.route('/new', methods=['GET', 'POST'])
def new_message():
    if request.method == 'POST':
        # Check CAPTCHA if enabled
        captcha_settings = get_captcha_settings()
        if captcha_settings['enabled'] and captcha_settings['message_enabled']:
            challenge_id = request.form.get('captcha_challenge_id')
            user_answer = request.form.get('captcha_answer')
            
            if not validate_captcha(challenge_id, user_answer):
                # Generate new CAPTCHA for retry
                captcha = generate_captcha()
                return render_template('new_message.html', 
                                     user_name=request.cookies.get('user_name', ''),
                                     captcha=captcha,
                                     error='Incorrect CAPTCHA answer. Please try again.')
        
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
                    filepath = os.path.join(current_app.config['MESSAGE_UPLOAD_FOLDER'], filename)
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
                        file_path = os.path.join(current_app.config['MESSAGE_UPLOAD_FOLDER'], photo_filename)
                        description = f"Message photo by {message.author_name}"
                        if message.content:
                            description += f" - {message.content[:100]}"
                        sync_file_to_immich(file_path, photo_filename, description)
                except Exception as e:
                    print(f"Error syncing message photo to Immich: {e}")
            
            # Save user name in cookie
            resp = make_response(redirect(url_for('messages.message_board')))
            resp.set_cookie('user_name', author_name, max_age=30*24*60*60)  # 30 days
            resp.set_cookie('user_identifier', user_identifier, max_age=365*24*60*60)  # 1 year
            return resp
        else:
            return render_template('new_message.html', 
                                 user_name=request.cookies.get('user_name', ''),
                                 error='Message content is required')
    
    user_name = request.cookies.get('user_name', '')
    captcha_settings = get_captcha_settings()
    
    # Generate CAPTCHA if enabled
    captcha = None
    if captcha_settings['enabled'] and captcha_settings['message_enabled']:
        captcha = generate_captcha()
    
    return render_template('new_message.html', user_name=user_name, captcha=captcha) 