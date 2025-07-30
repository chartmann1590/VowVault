from flask import Blueprint, render_template, request, jsonify, redirect, url_for, flash
from app.models import Photo, PhotoOfDay, PhotoOfDayVote, PhotoOfDayCandidate, Settings
from app import db
from datetime import datetime, date, timedelta
import json

photo_of_day_bp = Blueprint('photo_of_day', __name__)

def get_likes_threshold():
    """Get the likes threshold for automatic candidate selection"""
    threshold = Settings.get('photo_of_day_likes_threshold', '3')
    return int(threshold)

def add_automatic_candidates():
    """Add photos with enough likes as candidates automatically"""
    threshold = get_likes_threshold()
    
    # Find photos with enough likes that aren't already candidates
    photos_to_add = Photo.query.filter(
        Photo.likes >= threshold
    ).all()
    
    added_count = 0
    for photo in photos_to_add:
        # Check if already a candidate
        existing = PhotoOfDayCandidate.query.filter_by(photo_id=photo.id).first()
        if not existing:
            candidate = PhotoOfDayCandidate(
                photo_id=photo.id,
                date_added=date.today(),
                is_selected=False
            )
            db.session.add(candidate)
            added_count += 1
    
    if added_count > 0:
        db.session.commit()
    
    return added_count

@photo_of_day_bp.route('/photo-of-day')
def photo_of_day():
    """Main Photo of the Day page"""
    # Get or create user identifier
    user_identifier = request.cookies.get('user_identifier')
    user_name = request.cookies.get('user_name', 'Anonymous')
    
    # Get today's photo of the day
    today = date.today()
    today_photo = PhotoOfDay.query.filter_by(date=today, is_active=True).first()
    
    # Get recent photos of the day (last 7 days)
    recent_photos = PhotoOfDay.query.filter(
        PhotoOfDay.date >= today - timedelta(days=7),
        PhotoOfDay.is_active == True
    ).order_by(PhotoOfDay.date.desc()).all()
    
    # Get user's vote for today if it exists
    user_vote = None
    if today_photo and user_identifier:
        user_vote = PhotoOfDayVote.query.filter_by(
            photo_of_day_id=today_photo.id,
            user_identifier=user_identifier
        ).first()
    
    return render_template('photo_of_day.html',
                         today_photo=today_photo,
                         recent_photos=recent_photos,
                         user_vote=user_vote,
                         user_identifier=user_identifier,
                         user_name=user_name)

@photo_of_day_bp.route('/api/photo-of-day/vote', methods=['POST'])
def vote_photo_of_day():
    """Vote for the current Photo of the Day"""
    data = request.get_json()
    user_identifier = request.cookies.get('user_identifier')
    user_name = request.cookies.get('user_name', 'Anonymous')
    
    if not user_identifier:
        return jsonify({'success': False, 'message': 'User identifier required'}), 400
    
    today = date.today()
    today_photo = PhotoOfDay.query.filter_by(date=today, is_active=True).first()
    
    if not today_photo:
        return jsonify({'success': False, 'message': 'No photo of the day found for today'}), 404
    
    # Check if user already voted
    existing_vote = PhotoOfDayVote.query.filter_by(
        photo_of_day_id=today_photo.id,
        user_identifier=user_identifier
    ).first()
    
    if existing_vote:
        return jsonify({'success': False, 'message': 'You have already voted for today\'s photo'}), 400
    
    # Create new vote
    vote = PhotoOfDayVote(
        photo_of_day_id=today_photo.id,
        user_identifier=user_identifier,
        user_name=user_name
    )
    
    db.session.add(vote)
    db.session.commit()
    
    return jsonify({
        'success': True,
        'message': 'Vote recorded successfully!',
        'vote_count': today_photo.vote_count
    })

@photo_of_day_bp.route('/api/photo-of-day/unvote', methods=['POST'])
def unvote_photo_of_day():
    """Remove vote for the current Photo of the Day"""
    user_identifier = request.cookies.get('user_identifier')
    
    if not user_identifier:
        return jsonify({'success': False, 'message': 'User identifier required'}), 400
    
    today = date.today()
    today_photo = PhotoOfDay.query.filter_by(date=today, is_active=True).first()
    
    if not today_photo:
        return jsonify({'success': False, 'message': 'No photo of the day found for today'}), 404
    
    # Find and delete user's vote
    vote = PhotoOfDayVote.query.filter_by(
        photo_of_day_id=today_photo.id,
        user_identifier=user_identifier
    ).first()
    
    if not vote:
        return jsonify({'success': False, 'message': 'No vote found to remove'}), 404
    
    db.session.delete(vote)
    db.session.commit()
    
    return jsonify({
        'success': True,
        'message': 'Vote removed successfully!',
        'vote_count': today_photo.vote_count
    })

@photo_of_day_bp.route('/admin/photo-of-day')
def admin_photo_of_day():
    """Admin interface for managing Photo of the Day"""
    # Check admin access (you'll need to implement this based on your auth system)
    admin_key = request.args.get('key')
    if admin_key != 'wedding2024':  # Replace with your actual admin key
        return redirect(url_for('main.index'))
    
    # Get all photos of the day
    photos_of_day = PhotoOfDay.query.order_by(PhotoOfDay.date.desc()).all()
    
    # Get candidate photos (photos that could be selected)
    candidate_photos = PhotoOfDayCandidate.query.order_by(PhotoOfDayCandidate.date_added.desc()).all()
    
    # Get all photos for selection
    all_photos = Photo.query.order_by(Photo.upload_date.desc()).limit(100).all()
    
    # Get current settings
    likes_threshold = get_likes_threshold()
    
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

@photo_of_day_bp.route('/admin/photo-of-day/select', methods=['POST'])
def select_photo_of_day():
    """Select a photo as Photo of the Day"""
    admin_key = request.args.get('key')
    if admin_key != 'wedding2024':
        return jsonify({'success': False, 'message': 'Unauthorized'}), 403
    
    data = request.get_json()
    photo_id = data.get('photo_id')
    selected_date = data.get('date')
    
    if not photo_id or not selected_date:
        return jsonify({'success': False, 'message': 'Photo ID and date required'}), 400
    
    try:
        selected_date = datetime.strptime(selected_date, '%Y-%m-%d').date()
    except ValueError:
        return jsonify({'success': False, 'message': 'Invalid date format'}), 400
    
    # Check if photo exists
    photo = Photo.query.get(photo_id)
    if not photo:
        return jsonify({'success': False, 'message': 'Photo not found'}), 404
    
    # Check if there's already a photo of the day for this date
    existing = PhotoOfDay.query.filter_by(date=selected_date).first()
    if existing:
        return jsonify({'success': False, 'message': 'Photo of the day already exists for this date'}), 400
    
    # Create new Photo of the Day
    photo_of_day = PhotoOfDay(
        photo_id=photo_id,
        date=selected_date,
        is_active=True
    )
    
    db.session.add(photo_of_day)
    db.session.commit()
    
    return jsonify({'success': True, 'message': 'Photo of the day selected successfully!'})

@photo_of_day_bp.route('/admin/photo-of-day/delete/<int:photo_of_day_id>', methods=['POST'])
def delete_photo_of_day(photo_of_day_id):
    """Delete a Photo of the Day"""
    admin_key = request.args.get('key')
    if admin_key != 'wedding2024':
        return jsonify({'success': False, 'message': 'Unauthorized'}), 403
    
    photo_of_day = PhotoOfDay.query.get(photo_of_day_id)
    if not photo_of_day:
        return jsonify({'success': False, 'message': 'Photo of the day not found'}), 404
    
    db.session.delete(photo_of_day)
    db.session.commit()
    
    return jsonify({'success': True, 'message': 'Photo of the day deleted successfully!'})

@photo_of_day_bp.route('/admin/photo-of-day/add-candidate', methods=['POST'])
def add_photo_candidate():
    """Add a photo as a candidate for Photo of the Day"""
    admin_key = request.args.get('key')
    if admin_key != 'wedding2024':
        return jsonify({'success': False, 'message': 'Unauthorized'}), 403
    
    data = request.get_json()
    photo_id = data.get('photo_id')
    
    if not photo_id:
        return jsonify({'success': False, 'message': 'Photo ID required'}), 400
    
    # Check if photo exists
    photo = Photo.query.get(photo_id)
    if not photo:
        return jsonify({'success': False, 'message': 'Photo not found'}), 404
    
    # Check if already a candidate
    existing = PhotoOfDayCandidate.query.filter_by(photo_id=photo_id).first()
    if existing:
        return jsonify({'success': False, 'message': 'Photo is already a candidate'}), 400
    
    # Add as candidate
    candidate = PhotoOfDayCandidate(
        photo_id=photo_id,
        date_added=date.today()
    )
    
    db.session.add(candidate)
    db.session.commit()
    
    return jsonify({'success': True, 'message': 'Photo added as candidate successfully!'})

@photo_of_day_bp.route('/admin/photo-of-day/update-threshold', methods=['POST'])
def update_likes_threshold():
    """Update the likes threshold for automatic candidates"""
    admin_key = request.args.get('key')
    if admin_key != 'wedding2024':
        return jsonify({'success': False, 'message': 'Unauthorized'}), 403
    
    data = request.get_json()
    threshold = data.get('threshold')
    
    if not threshold or not threshold.isdigit():
        return jsonify({'success': False, 'message': 'Valid threshold required'}), 400
    
    threshold = int(threshold)
    if threshold < 1:
        return jsonify({'success': False, 'message': 'Threshold must be at least 1'}), 400
    
    # Update the setting
    Settings.set('photo_of_day_likes_threshold', str(threshold))
    
    return jsonify({'success': True, 'message': f'Likes threshold updated to {threshold}'})

@photo_of_day_bp.route('/admin/photo-of-day/add-auto-candidates', methods=['POST'])
def add_automatic_candidates_route():
    """Manually trigger adding automatic candidates"""
    admin_key = request.args.get('key')
    if admin_key != 'wedding2024':
        return jsonify({'success': False, 'message': 'Unauthorized'}), 403
    
    added_count = add_automatic_candidates()
    
    return jsonify({
        'success': True, 
        'message': f'Added {added_count} photos as automatic candidates'
    })

@photo_of_day_bp.route('/api/photo-of-day/stats')
def photo_of_day_stats():
    """Get statistics for Photo of the Day"""
    today = date.today()
    today_photo = PhotoOfDay.query.filter_by(date=today, is_active=True).first()
    
    if not today_photo:
        return jsonify({'success': False, 'message': 'No photo of the day for today'})
    
    user_identifier = request.cookies.get('user_identifier')
    has_voted = False
    
    if user_identifier:
        vote = PhotoOfDayVote.query.filter_by(
            photo_of_day_id=today_photo.id,
            user_identifier=user_identifier
        ).first()
        has_voted = vote is not None
    
    return jsonify({
        'success': True,
        'vote_count': today_photo.vote_count,
        'unique_voters': today_photo.unique_voters,
        'has_voted': has_voted
    }) 