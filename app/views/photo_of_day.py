from flask import Blueprint, render_template, request, jsonify, redirect, url_for, flash
from app.models.photo import Photo
from app.models.settings import Settings
from app.models.photo_of_day import PhotoOfDay, PhotoOfDayVote, PhotoOfDayCandidate, PhotoOfDayContest
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
            # Get or create today's contest
            today = date.today()
            contest = PhotoOfDayContest.query.filter_by(contest_date=today).first()
            if not contest:
                contest = PhotoOfDayContest(contest_date=today, is_active=True)
                db.session.add(contest)
                db.session.flush()  # Get the ID
            
            candidate = PhotoOfDayCandidate(
                photo_id=photo.id,
                contest_id=contest.id,
                date_added=today,
                is_winner=False
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
    
    # Get today's contest
    today = date.today()
    today_contest = PhotoOfDayContest.query.filter_by(contest_date=today, is_active=True).first()
    
    # Get recent contests (last 7 days)
    recent_contests = PhotoOfDayContest.query.filter(
        PhotoOfDayContest.contest_date >= today - timedelta(days=7),
        PhotoOfDayContest.is_active == True
    ).order_by(PhotoOfDayContest.contest_date.desc()).all()
    
    # Get user's vote for today if it exists
    user_vote = None
    if today_contest and user_identifier:
        user_vote = PhotoOfDayVote.query.filter_by(
            contest_id=today_contest.id,
            user_identifier=user_identifier
        ).first()
    
    return render_template('photo_of_day.html',
                         today_contest=today_contest,
                         recent_contests=recent_contests,
                         user_vote=user_vote,
                         user_identifier=user_identifier,
                         user_name=user_name)

@photo_of_day_bp.route('/api/photo-of-day/vote', methods=['POST'])
def vote_photo_of_day():
    """Vote for a candidate in the current Photo of the Day contest"""
    data = request.get_json()
    user_identifier = request.cookies.get('user_identifier')
    user_name = request.cookies.get('user_name', 'Anonymous')
    
    if not user_identifier:
        return jsonify({'success': False, 'message': 'User identifier required'}), 400
    
    candidate_id = data.get('candidate_id')
    if not candidate_id:
        return jsonify({'success': False, 'message': 'Candidate ID required'}), 400
    
    today = date.today()
    today_contest = PhotoOfDayContest.query.filter_by(contest_date=today, is_active=True).first()
    
    if not today_contest:
        return jsonify({'success': False, 'message': 'No contest found for today'}), 404
    
    # Check if candidate exists and belongs to today's contest
    candidate = PhotoOfDayCandidate.query.filter_by(
        id=candidate_id,
        contest_id=today_contest.id
    ).first()
    
    if not candidate:
        return jsonify({'success': False, 'message': 'Invalid candidate'}), 404
    
    # Check if voting is still open
    if not today_contest.is_voting_open:
        return jsonify({'success': False, 'message': 'Voting has closed for today'}), 400
    
    # Check if user already voted
    existing_vote = PhotoOfDayVote.query.filter_by(
        contest_id=today_contest.id,
        user_identifier=user_identifier
    ).first()
    
    if existing_vote:
        return jsonify({'success': False, 'message': 'You have already voted in today\'s contest'}), 400
    
    # Create new vote
    vote = PhotoOfDayVote(
        contest_id=today_contest.id,
        candidate_id=candidate_id,
        user_identifier=user_identifier,
        user_name=user_name
    )
    
    db.session.add(vote)
    db.session.commit()
    
    return jsonify({
        'success': True,
        'message': 'Vote recorded successfully!',
        'vote_count': candidate.vote_count
    })

@photo_of_day_bp.route('/api/photo-of-day/unvote', methods=['POST'])
def unvote_photo_of_day():
    """Remove vote for the current Photo of the Day contest"""
    user_identifier = request.cookies.get('user_identifier')
    
    if not user_identifier:
        return jsonify({'success': False, 'message': 'User identifier required'}), 400
    
    today = date.today()
    today_contest = PhotoOfDayContest.query.filter_by(contest_date=today, is_active=True).first()
    
    if not today_contest:
        return jsonify({'success': False, 'message': 'No contest found for today'}), 404
    
    # Find and delete user's vote
    vote = PhotoOfDayVote.query.filter_by(
        contest_id=today_contest.id,
        user_identifier=user_identifier
    ).first()
    
    if not vote:
        return jsonify({'success': False, 'message': 'No vote found to remove'}), 404
    
    db.session.delete(vote)
    db.session.commit()
    
    return jsonify({
        'success': True,
        'message': 'Vote removed successfully!'
    })

@photo_of_day_bp.route('/admin/photo-of-day')
def admin_photo_of_day():
    """Admin interface for managing Photo of the Day contests"""
    # Check admin access (you'll need to implement this based on your auth system)
    admin_key = request.args.get('key')
    if admin_key != 'wedding2024':  # Replace with your actual admin key
        return redirect(url_for('main.index'))
    
    # Get all contests
    contests = PhotoOfDayContest.query.order_by(PhotoOfDayContest.contest_date.desc()).all()
    
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
                         contests=contests,
                         candidate_photos=candidate_photos,
                         all_photos=all_photos,
                         likes_threshold=likes_threshold,
                         auto_candidate_photos=auto_candidate_photos,
                         today_date=date.today().isoformat())

@photo_of_day_bp.route('/admin/photo-of-day/create-contest', methods=['POST'])
def create_contest():
    """Create a new Photo of the Day contest"""
    admin_key = request.args.get('key')
    if admin_key != 'wedding2024':
        return jsonify({'success': False, 'message': 'Unauthorized'}), 403
    
    try:
        data = request.get_json()
    except Exception as e:
        return jsonify({'success': False, 'message': f'Invalid JSON data: {str(e)}'}), 400
    
    if not data:
        return jsonify({'success': False, 'message': 'No JSON data provided'}), 400
    
    contest_date = data.get('contest_date')
    voting_ends_at = data.get('voting_ends_at')
    
    if not contest_date:
        return jsonify({'success': False, 'message': 'Contest date required'}), 400
    
    try:
        contest_date = datetime.strptime(contest_date, '%Y-%m-%d').date()
    except ValueError:
        return jsonify({'success': False, 'message': 'Invalid date format'}), 400
    
    # Check if contest already exists for this date
    existing = PhotoOfDayContest.query.filter_by(contest_date=contest_date).first()
    if existing:
        return jsonify({'success': False, 'message': 'Contest already exists for this date'}), 400
    
    # Parse voting end time if provided
    voting_end_datetime = None
    if voting_ends_at:
        try:
            voting_end_datetime = datetime.strptime(voting_ends_at, '%Y-%m-%d %H:%M')
        except ValueError:
            return jsonify({'success': False, 'message': 'Invalid voting end time format'}), 400
    
    # Create new contest
    contest = PhotoOfDayContest(
        contest_date=contest_date,
        is_active=True,
        voting_ends_at=voting_end_datetime
    )
    
    db.session.add(contest)
    db.session.commit()
    
    return jsonify({'success': True, 'message': 'Contest created successfully!'})

@photo_of_day_bp.route('/admin/photo-of-day/select-winner', methods=['POST'])
def select_winner():
    """Select a winner for a contest"""
    admin_key = request.args.get('key')
    if admin_key != 'wedding2024':
        return jsonify({'success': False, 'message': 'Unauthorized'}), 403
    
    try:
        data = request.get_json()
    except Exception as e:
        return jsonify({'success': False, 'message': f'Invalid JSON data: {str(e)}'}), 400
    
    if not data:
        return jsonify({'success': False, 'message': 'No JSON data provided'}), 400
    
    contest_id = data.get('contest_id')
    candidate_id = data.get('candidate_id')
    
    if not contest_id or not candidate_id:
        return jsonify({'success': False, 'message': 'Contest ID and candidate ID required'}), 400
    
    # Check if contest exists
    contest = PhotoOfDayContest.query.get(contest_id)
    if not contest:
        return jsonify({'success': False, 'message': 'Contest not found'}), 404
    
    # Check if candidate exists and belongs to this contest
    candidate = PhotoOfDayCandidate.query.filter_by(
        id=candidate_id,
        contest_id=contest_id
    ).first()
    
    if not candidate:
        return jsonify({'success': False, 'message': 'Candidate not found'}), 404
    
    # Set the winner
    contest.winner_photo_id = candidate.photo_id
    candidate.is_winner = True
    
    db.session.commit()
    
    return jsonify({'success': True, 'message': 'Winner selected successfully!'})

@photo_of_day_bp.route('/admin/photo-of-day/delete-contest/<int:contest_id>', methods=['POST'])
def delete_contest(contest_id):
    """Delete a Photo of the Day contest"""
    admin_key = request.args.get('key')
    if admin_key != 'wedding2024':
        return jsonify({'success': False, 'message': 'Unauthorized'}), 403
    
    contest = PhotoOfDayContest.query.get(contest_id)
    if not contest:
        return jsonify({'success': False, 'message': 'Contest not found'}), 404
    
    db.session.delete(contest)
    db.session.commit()
    
    return jsonify({'success': True, 'message': 'Contest deleted successfully!'})

@photo_of_day_bp.route('/admin/photo-of-day/add-candidate', methods=['POST'])
def add_photo_candidate():
    """Add a photo as a candidate for Photo of the Day"""
    admin_key = request.args.get('key')
    if admin_key != 'wedding2024':
        return jsonify({'success': False, 'message': 'Unauthorized'}), 403
    
    try:
        data = request.get_json()
    except Exception as e:
        return jsonify({'success': False, 'message': 'Invalid JSON data'}), 400
    
    if not data:
        return jsonify({'success': False, 'message': 'No JSON data provided'}), 400
    
    photo_id = data.get('photo_id')
    
    if not photo_id:
        return jsonify({'success': False, 'message': 'Photo ID required'}), 400
    
    # Check if photo exists
    photo = Photo.query.get(photo_id)
    if not photo:
        return jsonify({'success': False, 'message': 'Photo not found'}), 404
    
    # Get or create today's contest
    today = date.today()
    contest = PhotoOfDayContest.query.filter_by(contest_date=today).first()
    if not contest:
        contest = PhotoOfDayContest(contest_date=today, is_active=True)
        db.session.add(contest)
        db.session.flush()  # Get the ID
    
    # Check if already a candidate
    existing = PhotoOfDayCandidate.query.filter_by(
        photo_id=photo_id,
        contest_id=contest.id
    ).first()
    
    if existing:
        return jsonify({'success': False, 'message': 'Photo is already a candidate for this contest'}), 400
    
    # Add as candidate
    candidate = PhotoOfDayCandidate(
        photo_id=photo_id,
        contest_id=contest.id,
        date_added=today,
        is_winner=False
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
    """Get statistics for Photo of the Day contest"""
    today = date.today()
    today_contest = PhotoOfDayContest.query.filter_by(contest_date=today, is_active=True).first()
    
    if not today_contest:
        return jsonify({'success': False, 'message': 'No contest for today'})
    
    user_identifier = request.cookies.get('user_identifier')
    has_voted = False
    
    if user_identifier:
        vote = PhotoOfDayVote.query.filter_by(
            contest_id=today_contest.id,
            user_identifier=user_identifier
        ).first()
        has_voted = vote is not None
    
    return jsonify({
        'success': True,
        'total_votes': today_contest.total_votes,
        'unique_voters': today_contest.unique_voters,
        'has_voted': has_voted,
        'is_voting_open': today_contest.is_voting_open
    }) 