from flask import Blueprint, render_template, request, jsonify, make_response
import json
import secrets
from app.models.photo import Photo
from app.models.settings import Settings
from app.utils.settings_utils import get_email_settings
from app.utils.db_optimization import db_optimizer, cached_query
from app import db

main_bp = Blueprint('main', __name__)

@main_bp.route('/')
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
    
    # For lazy loading, we'll only load initial photos on the server
    # The rest will be loaded via JavaScript API calls
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
    @cached_query(ttl=1800)  # Cache for 30 minutes
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

@main_bp.route('/api/photos')
def api_photos():
    """API endpoint for lazy loading photos with optimized queries"""
    page = request.args.get('page', 1, type=int)
    per_page = request.args.get('per_page', 20, type=int)  # Increased for better performance
    
    # Get search parameters
    search_query = request.args.get('search', '').strip()
    media_filter = request.args.get('media_type', '')
    tag_filter = request.args.get('tag', '')
    
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
    
    # Convert photos to JSON-serializable format
    photos_data = []
    for photo in photos.items:
        photo_data = {
            'id': photo.id,
            'filename': photo.filename,
            'thumbnail_filename': photo.thumbnail_filename,
            'uploader_name': photo.uploader_name,
            'upload_date': photo.upload_date.strftime('%b %d, %Y'),
            'description': photo.description,
            'tags': photo.tags,
            'media_type': photo.media_type,
            'is_photobooth': photo.is_photobooth,
            'duration': photo.duration,
            'likes': photo.likes,
            'comments_count': len(photo.comments),
            'url': f'/photo/{photo.id}'
        }
        photos_data.append(photo_data)
    
    return jsonify({
        'photos': photos_data,
        'has_next': photos.has_next,
        'has_prev': photos.has_prev,
        'page': photos.page,
        'pages': photos.pages,
        'total': photos.total,
        'per_page': photos.per_page
    })

@main_bp.route('/photo/<int:photo_id>')
def view_photo(photo_id):
    from app.models.photo import Photo, Like
    photo = Photo.query.get_or_404(photo_id)
    user_name = request.cookies.get('user_name', '')
    user_identifier = request.cookies.get('user_identifier', '')
    
    # Check if user has liked this photo
    has_liked = False
    if user_identifier:
        has_liked = Like.query.filter_by(photo_id=photo_id, user_identifier=user_identifier).first() is not None
    
    return render_template('photo_detail.html', photo=photo, user_name=user_name, has_liked=has_liked)

@main_bp.route('/api/mark-welcome-seen', methods=['POST'])
def mark_welcome_seen():
    resp = jsonify({'success': True})
    resp.set_cookie('has_seen_welcome', 'true', max_age=365*24*60*60)  # 1 year
    return resp

@main_bp.route('/privacy-policy')
def privacy_policy():
    from datetime import datetime
    current_date = datetime.now().strftime('%B %d, %Y')
    return render_template('privacy_policy.html', current_date=current_date)

@main_bp.route('/terms-of-use')
def terms_of_use():
    from datetime import datetime
    current_date = datetime.now().strftime('%B %d, %Y')
    return render_template('terms_of_use.html', current_date=current_date)

@main_bp.route('/sw.js')
def serve_service_worker():
    from flask import send_from_directory
    return send_from_directory('../static', 'sw.js', mimetype='application/javascript')

@main_bp.route('/static/manifest.json')
def serve_manifest():
    from flask import send_from_directory
    return send_from_directory('../static', 'manifest.json', mimetype='application/manifest+json')

@main_bp.route('/notifications')
def notifications_page():
    user_name = request.cookies.get('user_name', '')
    user_identifier = request.cookies.get('user_identifier', '')
    return render_template('notifications.html', user_name=user_name, user_identifier=user_identifier) 