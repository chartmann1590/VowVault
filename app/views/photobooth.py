from flask import Blueprint, render_template, request, jsonify, current_app
from datetime import datetime
import base64
import os
import secrets
from app.models.photo import Photo
from app import db
from app.utils.settings_utils import get_immich_settings
from app.utils.immich_utils import sync_file_to_immich
from app.models.settings import Settings
import json

photobooth_bp = Blueprint('photobooth', __name__)

@photobooth_bp.route('/')
def photobooth():
    user_name = request.cookies.get('user_name', '')
    
    # Get the current border settings
    border_settings = Settings.get('photobooth_border', '{}')
    border_settings = json.loads(border_settings) if border_settings else {}
    
    return render_template('photobooth.html', 
                         user_name=user_name,
                         border_url=border_settings.get('border_url', ''))

@photobooth_bp.route('/api/save', methods=['POST'])
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
        filepath = os.path.join(current_app.config['PHOTOBOOTH_FOLDER'], filename)
        
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
                    file_path = os.path.join(current_app.config['PHOTOBOOTH_FOLDER'], photo.filename)
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