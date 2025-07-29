from flask import Blueprint, render_template, request, make_response, redirect, url_for, current_app
from werkzeug.utils import secure_filename
from datetime import datetime
import os
from app.models.guestbook import GuestbookEntry
from app import db
from app.utils.file_utils import allowed_file
from app.utils.settings_utils import get_immich_settings
from app.utils.immich_utils import sync_file_to_immich

guestbook_bp = Blueprint('guestbook', __name__)

@guestbook_bp.route('/')
def guestbook():
    user_name = request.cookies.get('user_name', '')
    entries = GuestbookEntry.query.order_by(GuestbookEntry.created_at.desc()).all()
    return render_template('guestbook.html', user_name=user_name, entries=entries)

@guestbook_bp.route('/sign', methods=['GET', 'POST'])
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
                    filepath = os.path.join(current_app.config['GUESTBOOK_UPLOAD_FOLDER'], filename)
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
                        file_path = os.path.join(current_app.config['GUESTBOOK_UPLOAD_FOLDER'], photo_filename)
                        description = f"Guestbook photo by {entry.name} from {entry.location}"
                        if entry.message:
                            description += f" - {entry.message[:100]}"
                        sync_file_to_immich(file_path, photo_filename, description)
                except Exception as e:
                    print(f"Error syncing guestbook photo to Immich: {e}")
            
            # Save user name in cookie
            resp = make_response(redirect(url_for('guestbook.guestbook')))
            resp.set_cookie('user_name', name, max_age=30*24*60*60)  # 30 days
            return resp
        else:
            return render_template('sign_guestbook.html', 
                                 user_name=request.cookies.get('user_name', ''),
                                 error='Name and message are required')
    
    user_name = request.cookies.get('user_name', '')
    return render_template('sign_guestbook.html', user_name=user_name) 