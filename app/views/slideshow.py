from flask import Blueprint, render_template, jsonify, request
from app.models.photo import Photo
from app.models.guestbook import GuestbookEntry
from app.models.messages import Message
from app.models.slideshow import SlideshowSettings, SlideshowActivity
from app.utils.db_optimization import cached_query
from app import db
from datetime import datetime, timedelta
import json

slideshow_bp = Blueprint('slideshow', __name__)

@slideshow_bp.route('/slideshow')
def slideshow():
    """Main slideshow page"""
    # Get slideshow settings
    settings = get_slideshow_settings()
    
    return render_template('slideshow.html', settings=settings)

@slideshow_bp.route('/api/slideshow/activities')
def get_slideshow_activities():
    """API endpoint to get activities for slideshow"""
    # Get parameters
    hours_back = request.args.get('hours', 24, type=int)
    max_activities = request.args.get('max_activities', 50, type=int)
    show_photos = request.args.get('show_photos', 'true') == 'true'
    show_guestbook = request.args.get('show_guestbook', 'true') == 'true'
    show_messages = request.args.get('show_messages', 'true') == 'true'
    
    since_time = datetime.utcnow() - timedelta(hours=hours_back)
    
    activities = []
    
    # Get recent photos if enabled
    if show_photos:
        photos = Photo.query.filter(
            Photo.upload_date >= since_time
        ).order_by(Photo.upload_date.desc()).limit(max_activities).all()
        
        for photo in photos:
            activities.append({
                'type': 'photo',
                'id': photo.id,
                'content': {
                    'filename': photo.filename,
                    'uploader_name': photo.uploader_name,
                    'description': photo.description,
                    'upload_date': photo.upload_date.isoformat(),
                    'media_type': photo.media_type,
                    'is_photobooth': photo.is_photobooth
                },
                'timestamp': photo.upload_date.isoformat(),
                'summary': f"New photo uploaded by {photo.uploader_name}"
            })
    
    # Get recent guestbook entries if enabled
    if show_guestbook:
        guestbook_entries = GuestbookEntry.query.filter(
            GuestbookEntry.created_at >= since_time
        ).order_by(GuestbookEntry.created_at.desc()).limit(max_activities).all()
        
        for entry in guestbook_entries:
            activities.append({
                'type': 'guestbook',
                'id': entry.id,
                'content': {
                    'name': entry.name,
                    'message': entry.message,
                    'location': entry.location,
                    'photo_filename': entry.photo_filename,
                    'created_at': entry.created_at.isoformat()
                },
                'timestamp': entry.created_at.isoformat(),
                'summary': f"Guestbook entry from {entry.name}"
            })
    
    # Get recent messages if enabled
    if show_messages:
        messages = Message.query.filter(
            Message.created_at >= since_time,
            Message.is_hidden == False
        ).order_by(Message.created_at.desc()).limit(max_activities).all()
        
        for message in messages:
            activities.append({
                'type': 'message',
                'id': message.id,
                'content': {
                    'author_name': message.author_name,
                    'content': message.content,
                    'photo_filename': message.photo_filename,
                    'created_at': message.created_at.isoformat()
                },
                'timestamp': message.created_at.isoformat(),
                'summary': f"Message from {message.author_name}"
            })
    
    # Sort by timestamp (newest first)
    activities.sort(key=lambda x: x['timestamp'], reverse=True)
    
    return jsonify({
        'activities': activities,
        'total_count': len(activities),
        'last_updated': datetime.utcnow().isoformat()
    })

@slideshow_bp.route('/api/slideshow/settings', methods=['GET', 'POST'])
def slideshow_settings():
    """API endpoint for slideshow settings"""
    if request.method == 'POST':
        data = request.get_json()
        
        # Update settings
        for key, value in data.items():
            setting = SlideshowSettings.query.filter_by(key=key).first()
            if setting:
                setting.value = str(value)
            else:
                setting = SlideshowSettings(key=key, value=str(value))
                db.session.add(setting)
        
        db.session.commit()
        return jsonify({'status': 'success'})
    
    # GET request - return current settings
    settings = get_slideshow_settings()
    return jsonify(settings)

@cached_query(ttl=300)  # Cache for 5 minutes
def get_slideshow_settings():
    """Get slideshow settings with defaults"""
    settings = {}
    
    # Get all settings from database
    db_settings = SlideshowSettings.query.all()
    for setting in db_settings:
        settings[setting.key] = setting.value
    
    # Set defaults if not present
    defaults = {
        'slideshow_interval': '5000',  # 5 seconds
        'transition_effect': 'fade',
        'show_photos': 'true',
        'show_guestbook': 'true',
        'show_messages': 'true',
        'auto_refresh': 'true',
        'refresh_interval': '900000',  # 15 minutes
        'max_activities': '50',
        'time_range_hours': '24',
        'enabled': 'true',
        'speed': '3',
        'effect': 'fade',
        'order': 'random',
        'max_photos': '20',
        'autoplay': 'true',
        'loop': 'true',
        'show_controls': 'true'
    }
    
    for key, default_value in defaults.items():
        if key not in settings:
            settings[key] = default_value
    
    return settings 