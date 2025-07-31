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
            # Get or create the main ongoing contest
            main_contest = PhotoOfDayContest.query.filter_by(is_active=True).first()
            if not main_contest:
                main_contest = PhotoOfDayContest(contest_date=date.today(), is_active=True)
                db.session.add(main_contest)
                db.session.flush()  # Get the ID
            
            candidate = PhotoOfDayCandidate(
                photo_id=photo.id,
                contest_id=main_contest.id,
                date_added=date.today(),
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
    
    # Get the main ongoing contest
    main_contest = PhotoOfDayContest.query.filter_by(is_active=True).first()
    
    # Get recent winners (last 10 winners)
    recent_winners = PhotoOfDayCandidate.query.filter_by(is_winner=True).order_by(
        PhotoOfDayCandidate.date_added.desc()
    ).limit(10).all()
    
    # Get user's vote for the main contest if it exists
    user_vote = None
    if main_contest and user_identifier:
        user_vote = PhotoOfDayVote.query.filter_by(
            contest_id=main_contest.id,
            user_identifier=user_identifier
        ).first()
    
    return render_template('photo_of_day.html',
                         main_contest=main_contest,
                         recent_winners=recent_winners,
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
    
    # Get the main ongoing contest
    main_contest = PhotoOfDayContest.query.filter_by(is_active=True).first()
    
    if not main_contest:
        return jsonify({'success': False, 'message': 'No active contest found'}), 404
    
    # Check if candidate exists and belongs to the main contest
    candidate = PhotoOfDayCandidate.query.filter_by(
        id=candidate_id,
        contest_id=main_contest.id
    ).first()
    
    if not candidate:
        return jsonify({'success': False, 'message': 'Invalid candidate'}), 404
    
    # Check if voting is still open
    if not main_contest.is_voting_open:
        return jsonify({'success': False, 'message': 'Voting has closed'}), 400
    
    # Check if user already voted
    existing_vote = PhotoOfDayVote.query.filter_by(
        contest_id=main_contest.id,
        user_identifier=user_identifier
    ).first()
    
    if existing_vote:
        return jsonify({'success': False, 'message': 'You have already voted'}), 400
    
    # Create new vote
    vote = PhotoOfDayVote(
        contest_id=main_contest.id,
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
    
    # Get the main ongoing contest
    main_contest = PhotoOfDayContest.query.filter_by(is_active=True).first()
    
    if not main_contest:
        return jsonify({'success': False, 'message': 'No active contest found'}), 404
    
    # Find and delete user's vote
    vote = PhotoOfDayVote.query.filter_by(
        contest_id=main_contest.id,
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
    
    # Get the main active contest
    main_contest = PhotoOfDayContest.query.filter_by(is_active=True).first()
    print(f"DEBUG: Main contest found: {main_contest}")  # Debug line
    
    # Get all contests for history
    all_contests = PhotoOfDayContest.query.order_by(PhotoOfDayContest.contest_date.desc()).all()
    print(f"DEBUG: Total contests in database: {len(all_contests)}")  # Debug line
    
    # Debug: Check all contests and their active status
    for i, contest in enumerate(all_contests):
        print(f"DEBUG: Contest {i+1}: ID={contest.id}, Active={contest.is_active}, Date={contest.contest_date}")
    
    # Get candidate photos for the main contest
    main_candidates = []
    if main_contest:
        main_candidates = PhotoOfDayCandidate.query.filter_by(contest_id=main_contest.id).order_by(PhotoOfDayCandidate.date_added.desc()).all()
        print(f"DEBUG: Main contest candidates: {len(main_candidates)}")  # Debug line
    else:
        print("DEBUG: No main contest found")  # Debug line
    
    # Get all photos for selection
    all_photos = Photo.query.order_by(Photo.upload_date.desc()).limit(100).all()
    
    # Get current settings
    likes_threshold = get_likes_threshold()
    
    # Get photos that would be auto-candidates based on current threshold
    auto_candidate_photos = Photo.query.filter(
        Photo.likes >= likes_threshold
    ).order_by(Photo.likes.desc()).limit(20).all()
    
    return render_template('admin_photo_of_day.html',
                         main_contest=main_contest,
                         main_candidates=main_candidates,
                         all_contests=all_contests,
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
        print(f"DEBUG: Create contest received data: {data}")  # Debug line
    except Exception as e:
        print(f"DEBUG: Create contest JSON error: {e}")  # Debug line
        return jsonify({'success': False, 'message': f'Invalid JSON data: {str(e)}'}), 400
    
    # Allow empty data for main contest creation
    if data is None:
        data = {}
        print("DEBUG: Create contest - using empty data for main contest")  # Debug line
    
    # Check if there's already an active contest
    existing_active = PhotoOfDayContest.query.filter_by(is_active=True).first()
    print(f"DEBUG: Existing active contest check: {existing_active}")  # Debug line
    
    if existing_active:
        print(f"DEBUG: Found existing active contest ID: {existing_active.id}")  # Debug line
        return jsonify({'success': False, 'message': 'An active contest already exists. Please close the current contest first.'}), 400
    else:
        print("DEBUG: No existing active contest found")  # Debug line
    
    # Create new main contest
    contest = PhotoOfDayContest(
        contest_date=date.today(),
        is_active=True,
        voting_ends_at=None  # No end time for ongoing contest
    )
    
    db.session.add(contest)
    db.session.commit()
    
    print("DEBUG: Created new main contest successfully")  # Debug line
    return jsonify({'success': True, 'message': 'Main contest created successfully!'})

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

@photo_of_day_bp.route('/admin/photo-of-day/close-contest', methods=['POST'])
def close_contest():
    """Close the current active contest (set is_active=False)"""
    admin_key = request.args.get('key')
    if admin_key != 'wedding2024':
        return jsonify({'success': False, 'message': 'Unauthorized'}), 403
    
    main_contest = PhotoOfDayContest.query.filter_by(is_active=True).first()
    if not main_contest:
        return jsonify({'success': False, 'message': 'No active contest found'}), 404
    
    main_contest.is_active = False
    db.session.commit()
    
    print(f"DEBUG: Closed contest {main_contest.id}")  # Debug line
    return jsonify({'success': True, 'message': 'Contest closed successfully!'})

@photo_of_day_bp.route('/admin/photo-of-day/add-candidate', methods=['POST'])
def add_photo_candidate():
    """Add a photo as a candidate for Photo of the Day"""
    admin_key = request.args.get('key')
    if admin_key != 'wedding2024':
        return jsonify({'success': False, 'message': 'Unauthorized'}), 403
    
    try:
        data = request.get_json()
        print(f"DEBUG: Received data: {data}")  # Debug line
    except Exception as e:
        print(f"DEBUG: JSON error: {e}")  # Debug line
        return jsonify({'success': False, 'message': f'Invalid JSON data: {str(e)}'}), 400
    
    if not data:
        print("DEBUG: No data received")  # Debug line
        return jsonify({'success': False, 'message': 'No JSON data provided'}), 400
    
    photo_id = data.get('photo_id')
    print(f"DEBUG: Photo ID: {photo_id}")  # Debug line
    
    if not photo_id:
        return jsonify({'success': False, 'message': 'Photo ID required'}), 400
    
    # Check if photo exists
    photo = Photo.query.get(photo_id)
    if not photo:
        print(f"DEBUG: Photo {photo_id} not found")  # Debug line
        return jsonify({'success': False, 'message': 'Photo not found'}), 404
    
    print(f"DEBUG: Photo found: {photo.filename}")  # Debug line
    
    # Get or create the main ongoing contest
    main_contest = PhotoOfDayContest.query.filter_by(is_active=True).first()
    if not main_contest:
        print("DEBUG: Creating new main contest")  # Debug line
        main_contest = PhotoOfDayContest(contest_date=date.today(), is_active=True)
        db.session.add(main_contest)
        db.session.flush()  # Get the ID
    
    print(f"DEBUG: Using contest ID: {main_contest.id}")  # Debug line
    
    # Check if already a candidate
    existing = PhotoOfDayCandidate.query.filter_by(
        photo_id=photo_id,
        contest_id=main_contest.id
    ).first()
    
    if existing:
        print("DEBUG: Photo already a candidate")  # Debug line
        return jsonify({'success': False, 'message': 'Photo is already a candidate'}), 400
    
    # Add as candidate
    candidate = PhotoOfDayCandidate(
        photo_id=photo_id,
        contest_id=main_contest.id,
        date_added=date.today(),
        is_winner=False
    )
    
    db.session.add(candidate)
    db.session.commit()
    
    print("DEBUG: Successfully added candidate")  # Debug line
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

@photo_of_day_bp.route('/admin/photo-of-day/debug-db', methods=['GET'])
def debug_database():
    """Debug database state"""
    admin_key = request.args.get('key')
    if admin_key != 'wedding2024':
        return jsonify({'success': False, 'message': 'Unauthorized'}), 403
    
    # Get all contests
    all_contests = PhotoOfDayContest.query.all()
    contests_data = []
    
    for contest in all_contests:
        contests_data.append({
            'id': contest.id,
            'contest_date': contest.contest_date.isoformat(),
            'is_active': contest.is_active,
            'winner_photo_id': contest.winner_photo_id,
            'voting_ends_at': contest.voting_ends_at.isoformat() if contest.voting_ends_at else None
        })
    
    # Get all candidates
    all_candidates = PhotoOfDayCandidate.query.all()
    candidates_data = []
    
    for candidate in all_candidates:
        candidates_data.append({
            'id': candidate.id,
            'photo_id': candidate.photo_id,
            'contest_id': candidate.contest_id,
            'is_winner': candidate.is_winner,
            'date_added': candidate.date_added.isoformat()
        })
    
    return jsonify({
        'success': True,
        'contests': contests_data,
        'candidates': candidates_data,
        'total_contests': len(contests_data),
        'total_candidates': len(candidates_data)
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