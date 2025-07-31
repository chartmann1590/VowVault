from flask import Blueprint, render_template, request, jsonify, redirect, url_for, flash
from app.models.photo import Photo
from app.models.settings import Settings
from app.models.photo_of_day import PhotoOfDay, PhotoOfDayVote
from app import db
from datetime import datetime, date, timedelta
import json

photo_of_day_bp = Blueprint('photo_of_day', __name__)

@photo_of_day_bp.route('/photo-of-day')
def photo_of_day():
    """Main Photo of the Day page"""
    # Get or create user identifier
    user_identifier = request.cookies.get('user_identifier')
    user_name = request.cookies.get('user_name', 'Anonymous')
    
    # Get today's photos of the day (up to 3)
    today = date.today()
    todays_photos = PhotoOfDay.query.filter_by(date=today, is_active=True).order_by(PhotoOfDay.position).all()
    
    # Get recent photos of the day (last 10)
    recent_photos = PhotoOfDay.query.filter_by(is_active=True).order_by(
        PhotoOfDay.date.desc(), PhotoOfDay.position
    ).limit(10).all()
    
    # Get user's votes for today if they exist
    user_votes = []
    if todays_photos and user_identifier:
        for photo_of_day in todays_photos:
            vote = PhotoOfDayVote.query.filter_by(
                photo_of_day_id=photo_of_day.id,
                user_identifier=user_identifier
            ).first()
            user_votes.append(vote)
    
    return render_template('photo_of_day.html',
                         todays_photos=todays_photos,
                         recent_photos=recent_photos,
                         user_votes=user_votes,
                         user_identifier=user_identifier,
                         user_name=user_name)

@photo_of_day_bp.route('/api/photo-of-day/vote', methods=['POST'])
def vote_photo_of_day():
    """Vote for a specific Photo of the Day"""
    data = request.get_json()
    user_identifier = request.cookies.get('user_identifier')
    user_name = request.cookies.get('user_name', 'Anonymous')
    
    if not user_identifier:
        return jsonify({'success': False, 'message': 'User identifier required'}), 400
    
    photo_of_day_id = data.get('photo_of_day_id')
    if not photo_of_day_id:
        return jsonify({'success': False, 'message': 'Photo of the Day ID required'}), 400
    
    # Get the photo of the day
    photo_of_day = PhotoOfDay.query.get(photo_of_day_id)
    if not photo_of_day:
        return jsonify({'success': False, 'message': 'Photo of the Day not found'}), 404
    
    # Check if user already voted for this photo
    existing_vote = PhotoOfDayVote.query.filter_by(
        photo_of_day_id=photo_of_day_id,
        user_identifier=user_identifier
    ).first()
    
    if existing_vote:
        return jsonify({'success': False, 'message': 'You have already voted for this photo'}), 400
    
    # Create new vote
    vote = PhotoOfDayVote(
        photo_of_day_id=photo_of_day_id,
        user_identifier=user_identifier,
        user_name=user_name
    )
    
    db.session.add(vote)
    db.session.commit()
    
    # Get updated vote count
    vote_count = PhotoOfDayVote.query.filter_by(photo_of_day_id=photo_of_day_id).count()
    
    return jsonify({
        'success': True,
        'message': 'Vote recorded successfully!',
        'vote_count': vote_count
    })

@photo_of_day_bp.route('/api/photo-of-day/unvote', methods=['POST'])
def unvote_photo_of_day():
    """Remove vote for a specific Photo of the Day"""
    data = request.get_json()
    user_identifier = request.cookies.get('user_identifier')
    
    if not user_identifier:
        return jsonify({'success': False, 'message': 'User identifier required'}), 400
    
    photo_of_day_id = data.get('photo_of_day_id')
    if not photo_of_day_id:
        return jsonify({'success': False, 'message': 'Photo of the Day ID required'}), 400
    
    # Find and delete user's vote
    vote = PhotoOfDayVote.query.filter_by(
        photo_of_day_id=photo_of_day_id,
        user_identifier=user_identifier
    ).first()
    
    if not vote:
        return jsonify({'success': False, 'message': 'No vote found to remove'}), 404
    
    db.session.delete(vote)
    db.session.commit()
    
    # Get updated vote count
    vote_count = PhotoOfDayVote.query.filter_by(photo_of_day_id=photo_of_day_id).count()
    
    return jsonify({
        'success': True,
        'message': 'Vote removed successfully!',
        'vote_count': vote_count
    })

@photo_of_day_bp.route('/admin/photo-of-day')
def admin_photo_of_day():
    """Admin interface for managing Photo of the Day"""
    # Check admin access
    admin_key = request.args.get('key')
    if admin_key != 'wedding2024':
        return redirect(url_for('main.index'))
    
    # Get today's photos of the day
    today = date.today()
    todays_photos = PhotoOfDay.query.filter_by(date=today, is_active=True).order_by(PhotoOfDay.position).all()
    
    # Get recent photos of the day
    recent_photos = PhotoOfDay.query.filter_by(is_active=True).order_by(
        PhotoOfDay.date.desc(), PhotoOfDay.position
    ).limit(20).all()
    
    # Get all photos for selection, sorted by most likes first
    all_photos = Photo.query.order_by(Photo.likes.desc()).limit(100).all()
    
    # Get photos with most likes for suggestions
    top_photos = Photo.query.order_by(Photo.likes.desc()).limit(20).all()
    
    return render_template('admin_photo_of_day.html',
                         todays_photos=todays_photos,
                         recent_photos=recent_photos,
                         all_photos=all_photos,
                         top_photos=top_photos,
                         today_date=today)

@photo_of_day_bp.route('/admin/photo-of-day/set', methods=['POST'])
def set_photo_of_day():
    """Set a photo as Photo of the Day for today"""
    admin_key = request.args.get('key')
    if admin_key != 'wedding2024':
        flash('Unauthorized access', 'error')
        return redirect(url_for('photo_of_day.admin_photo_of_day', key=admin_key))
    
    # Handle both JSON and form data
    if request.is_json:
        data = request.get_json()
    else:
        data = request.form.to_dict()
    
    photo_id = data.get('photo_id')
    position = data.get('position', 1)  # Default to position 1
    
    if not photo_id:
        flash('Photo ID required', 'error')
        return redirect(url_for('photo_of_day.admin_photo_of_day', key=admin_key))
    
    # Check if photo exists
    photo = Photo.query.get(photo_id)
    if not photo:
        flash('Photo not found', 'error')
        return redirect(url_for('photo_of_day.admin_photo_of_day', key=admin_key))
    
    today = date.today()
    
    # Check if there's already a photo of the day for this position today
    existing = PhotoOfDay.query.filter_by(date=today, position=position).first()
    if existing:
        # Update existing
        existing.photo_id = photo_id
        existing.is_active = True
        flash(f'Updated Photo of the Day position {position} for {today} to "{photo.original_filename}"', 'success')
    else:
        # Create new
        photo_of_day = PhotoOfDay(
            photo_id=photo_id,
            date=today,
            position=position,
            is_active=True
        )
        db.session.add(photo_of_day)
        flash(f'Set Photo of the Day position {position} for {today} to "{photo.original_filename}"', 'success')
    
    db.session.commit()
    return redirect(url_for('photo_of_day.admin_photo_of_day', key=admin_key))

@photo_of_day_bp.route('/admin/photo-of-day/clear', methods=['POST'])
def clear_photo_of_day():
    """Clear today's Photos of the Day"""
    admin_key = request.args.get('key')
    if admin_key != 'wedding2024':
        flash('Unauthorized access', 'error')
        return redirect(url_for('photo_of_day.admin_photo_of_day', key=admin_key))
    
    today = date.today()
    todays_photos = PhotoOfDay.query.filter_by(date=today).all()
    
    if not todays_photos:
        flash(f'No Photos of the Day found for {today}', 'info')
        return redirect(url_for('photo_of_day.admin_photo_of_day', key=admin_key))
    
    # Delete all photos of the day and their votes
    for photo_of_day in todays_photos:
        PhotoOfDayVote.query.filter_by(photo_of_day_id=photo_of_day.id).delete()
        db.session.delete(photo_of_day)
    
    db.session.commit()
    
    flash(f'Cleared all Photos of the Day for {today}', 'success')
    return redirect(url_for('photo_of_day.admin_photo_of_day', key=admin_key))

@photo_of_day_bp.route('/admin/photo-of-day/delete/<int:photo_of_day_id>', methods=['POST'])
def delete_photo_of_day(photo_of_day_id):
    """Delete a specific Photo of the Day"""
    admin_key = request.args.get('key')
    if admin_key != 'wedding2024':
        flash('Unauthorized access', 'error')
        return redirect(url_for('photo_of_day.admin_photo_of_day', key=admin_key))
    
    photo_of_day = PhotoOfDay.query.get(photo_of_day_id)
    if not photo_of_day:
        flash('Photo of the Day not found', 'error')
        return redirect(url_for('photo_of_day.admin_photo_of_day', key=admin_key))
    
    # Delete all votes for this photo of the day
    PhotoOfDayVote.query.filter_by(photo_of_day_id=photo_of_day_id).delete()
    db.session.delete(photo_of_day)
    db.session.commit()
    
    flash(f'Deleted Photo of the Day for {photo_of_day.date}', 'success')
    return redirect(url_for('photo_of_day.admin_photo_of_day', key=admin_key))

@photo_of_day_bp.route('/api/photo-of-day/stats')
def photo_of_day_stats():
    """Get statistics for today's Photos of the Day"""
    today = date.today()
    todays_photos = PhotoOfDay.query.filter_by(date=today, is_active=True).order_by(PhotoOfDay.position).all()
    
    if not todays_photos:
        return jsonify({'success': False, 'message': 'No Photos of the Day for today'})
    
    user_identifier = request.cookies.get('user_identifier')
    stats = []
    
    for photo_of_day in todays_photos:
        has_voted = False
        if user_identifier:
            vote = PhotoOfDayVote.query.filter_by(
                photo_of_day_id=photo_of_day.id,
                user_identifier=user_identifier
            ).first()
            has_voted = vote is not None
        
        vote_count = PhotoOfDayVote.query.filter_by(photo_of_day_id=photo_of_day.id).count()
        
        stats.append({
            'photo_of_day_id': photo_of_day.id,
            'position': photo_of_day.position,
            'vote_count': vote_count,
            'has_voted': has_voted
        })
    
    return jsonify({
        'success': True,
        'photos': stats
    }) 