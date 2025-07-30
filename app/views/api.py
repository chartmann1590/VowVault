from flask import Blueprint, request, jsonify, current_app
import secrets
from app.models.photo import Photo, Comment, Like
from app.models.messages import Message, MessageComment, MessageLike
from app.models.notifications import Notification, NotificationUser
from app import db
from app.utils.notification_utils import create_notification_with_push
from datetime import datetime

api_bp = Blueprint('api', __name__)

@api_bp.route('/like/<int:photo_id>', methods=['POST'])
def toggle_like(photo_id):
    photo = Photo.query.get_or_404(photo_id)
    user_identifier = request.cookies.get('user_identifier', '')
    
    if not user_identifier:
        user_identifier = secrets.token_hex(16)
    
    existing_like = Like.query.filter_by(photo_id=photo_id, user_identifier=user_identifier).first()
    
    if existing_like:
        db.session.delete(existing_like)
        photo.likes = max(0, photo.likes - 1)
        liked = False
    else:
        new_like = Like(photo_id=photo_id, user_identifier=user_identifier)
        db.session.add(new_like)
        photo.likes += 1
        liked = True
    
    db.session.commit()
    
    # Create database notification for the photo uploader if someone else liked it
    if liked and photo.uploader_identifier and photo.uploader_identifier != user_identifier:
        liker_name = request.cookies.get('user_name', 'Anonymous')
        
        # Create notification with push notification
        create_notification_with_push(
            user_identifier=photo.uploader_identifier,
            title='❤️ New Like!',
            message=f'{liker_name} just liked your photo!',
            notification_type='like',
            content_type='photo',
            content_id=photo_id
        )
    
    # Prepare notification data for the photo uploader
    notification_data = {
        'type': 'like',
        'action': 'liked' if liked else 'unliked',
        'photo_id': photo_id,
        'photo_uploader': photo.uploader_name,
        'uploader_identifier': photo.uploader_identifier,
        'liker_identifier': user_identifier,
        'liker_name': request.cookies.get('user_name', 'Anonymous'),
        'total_likes': photo.likes
    }
    
    resp = jsonify({
        'likes': photo.likes, 
        'liked': liked,
        'notification_data': notification_data
    })
    resp.set_cookie('user_identifier', user_identifier, max_age=365*24*60*60)  # 1 year
    return resp

@api_bp.route('/comment/<int:photo_id>', methods=['POST'])
def add_comment(photo_id):
    photo = Photo.query.get_or_404(photo_id)
    data = request.get_json()
    
    commenter_name = data.get('commenter_name', 'Anonymous').strip() or 'Anonymous'
    content = data.get('content', '').strip()
    
    if not content:
        return jsonify({'error': 'Comment cannot be empty'}), 400
    
    comment = Comment(
        photo_id=photo_id,
        commenter_name=commenter_name,
        content=content
    )
    db.session.add(comment)
    db.session.commit()
    
    # Create database notification for the photo uploader if someone else commented
    user_identifier = request.cookies.get('user_identifier', '')
    if photo.uploader_identifier and photo.uploader_identifier != user_identifier:
        # Create notification with push notification
        create_notification_with_push(
            user_identifier=photo.uploader_identifier,
            title='💬 New Comment!',
            message=f'{commenter_name} commented on your photo!',
            notification_type='comment',
            content_type='photo',
            content_id=photo_id
        )
    
    # Prepare notification data for the photo uploader
    notification_data = {
        'type': 'comment',
        'photo_id': photo_id,
        'photo_uploader': photo.uploader_name,
        'uploader_identifier': photo.uploader_identifier,
        'commenter_name': commenter_name,
        'comment_content': content,
        'comment_id': comment.id
    }
    
    resp = jsonify({
        'id': comment.id,
        'commenter_name': comment.commenter_name,
        'content': comment.content,
        'created_at': comment.created_at.strftime('%B %d, %Y at %I:%M %p'),
        'notification_data': notification_data
    })
    resp.set_cookie('user_name', commenter_name, max_age=30*24*60*60)  # 30 days
    return resp

@api_bp.route('/message/<int:message_id>/like', methods=['POST'])
def toggle_message_like(message_id):
    message = Message.query.get_or_404(message_id)
    user_identifier = request.cookies.get('user_identifier', '')
    
    if not user_identifier:
        user_identifier = secrets.token_hex(16)
    
    existing_like = MessageLike.query.filter_by(message_id=message_id, user_identifier=user_identifier).first()
    
    if existing_like:
        db.session.delete(existing_like)
        message.likes = max(0, message.likes - 1)
        liked = False
    else:
        new_like = MessageLike(message_id=message_id, user_identifier=user_identifier)
        db.session.add(new_like)
        message.likes += 1
        liked = True
    
    db.session.commit()
    
    # Create database notification for the message author if someone else liked it
    if liked and message.author_identifier and message.author_identifier != user_identifier:
        liker_name = request.cookies.get('user_name', 'Anonymous')
        
        # Create notification with push notification
        create_notification_with_push(
            user_identifier=message.author_identifier,
            title='❤️ New Like!',
            message=f'{liker_name} just liked your message!',
            notification_type='like',
            content_type='message',
            content_id=message_id
        )
    
    # Prepare notification data for the message author
    notification_data = {
        'type': 'message_like',
        'action': 'liked' if liked else 'unliked',
        'message_id': message_id,
        'message_author': message.author_name,
        'author_identifier': message.author_identifier,
        'liker_identifier': user_identifier,
        'liker_name': request.cookies.get('user_name', 'Anonymous'),
        'total_likes': message.likes
    }
    
    resp = jsonify({
        'likes': message.likes, 
        'liked': liked,
        'notification_data': notification_data
    })
    resp.set_cookie('user_identifier', user_identifier, max_age=365*24*60*60)  # 1 year
    return resp

@api_bp.route('/message/<int:message_id>/comment', methods=['POST'])
def add_message_comment(message_id):
    message = Message.query.get_or_404(message_id)
    data = request.get_json()
    
    commenter_name = data.get('commenter_name', 'Anonymous').strip() or 'Anonymous'
    content = data.get('content', '').strip()
    
    if not content:
        return jsonify({'error': 'Comment cannot be empty'}), 400
    
    comment = MessageComment(
        message_id=message_id,
        commenter_name=commenter_name,
        content=content
    )
    db.session.add(comment)
    db.session.commit()
    
    # Create database notification for the message author if someone else commented
    user_identifier = request.cookies.get('user_identifier', '')
    if message.author_identifier and message.author_identifier != user_identifier:
        # Create notification with push notification
        create_notification_with_push(
            user_identifier=message.author_identifier,
            title='💬 New Comment!',
            message=f'{commenter_name} commented on your message!',
            notification_type='comment',
            content_type='message',
            content_id=message_id
        )
    
    # Prepare notification data for the message author
    notification_data = {
        'type': 'message_comment',
        'message_id': message_id,
        'message_author': message.author_name,
        'author_identifier': message.author_identifier,
        'commenter_name': commenter_name,
        'comment_content': content,
        'comment_id': comment.id
    }
    
    resp = jsonify({
        'id': comment.id,
        'commenter_name': comment.commenter_name,
        'content': comment.content,
        'created_at': comment.created_at.strftime('%B %d, %Y at %I:%M %p'),
        'notification_data': notification_data
    })
    resp.set_cookie('user_name', commenter_name, max_age=30*24*60*60)  # 30 days
    return resp

@api_bp.route('/notifications/check')
def check_notifications():
    user_identifier = request.cookies.get('user_identifier', '')
    if not user_identifier:
        return jsonify({'notifications': [], 'count': 0})
    
    # Get unread notifications
    notifications = Notification.query.filter_by(
        user_identifier=user_identifier,
        is_read=False
    ).order_by(Notification.created_at.desc()).limit(10).all()
    
    notification_list = []
    for notification in notifications:
        notification_list.append({
            'id': notification.id,
            'title': notification.title,
            'message': notification.message,
            'type': notification.notification_type,
            'created_at': notification.created_at.strftime('%B %d, %Y at %I:%M %p'),
            'content_type': notification.content_type,
            'content_id': notification.content_id
        })
    
    return jsonify({
        'notifications': notification_list,
        'count': len(notification_list)
    })

@api_bp.route('/notifications/mark-read', methods=['POST'])
def mark_notification_read():
    user_identifier = request.cookies.get('user_identifier', '')
    data = request.get_json()
    notification_id = data.get('notification_id')
    
    if not user_identifier or not notification_id:
        return jsonify({'success': False, 'error': 'Missing parameters'})
    
    notification = Notification.query.filter_by(
        id=notification_id,
        user_identifier=user_identifier
    ).first()
    
    if notification:
        notification.is_read = True
        notification.read_at = datetime.utcnow()
        db.session.commit()
        return jsonify({'success': True})
    
    return jsonify({'success': False, 'error': 'Notification not found'})

@api_bp.route('/notifications/mark-all-read', methods=['POST'])
def mark_all_notifications_read():
    user_identifier = request.cookies.get('user_identifier', '')
    
    if not user_identifier:
        return jsonify({'success': False, 'error': 'User identifier required'})
    
    # Mark all unread notifications as read
    unread_notifications = Notification.query.filter_by(
        user_identifier=user_identifier,
        is_read=False
    ).all()
    
    for notification in unread_notifications:
        notification.is_read = True
        notification.read_at = datetime.utcnow()
    
    db.session.commit()
    return jsonify({'success': True, 'count': len(unread_notifications)})

@api_bp.route('/notifications/delete', methods=['POST'])
def delete_notification():
    user_identifier = request.cookies.get('user_identifier', '')
    data = request.get_json()
    notification_id = data.get('notification_id')
    
    if not user_identifier or not notification_id:
        return jsonify({'success': False, 'error': 'Missing parameters'})
    
    notification = Notification.query.filter_by(
        id=notification_id,
        user_identifier=user_identifier
    ).first()
    
    if notification:
        db.session.delete(notification)
        db.session.commit()
        return jsonify({'success': True})
    
    return jsonify({'success': False, 'error': 'Notification not found'})

@api_bp.route('/notifications/toggle-enabled', methods=['POST'])
def toggle_notifications_enabled():
    user_identifier = request.cookies.get('user_identifier', '')
    data = request.get_json()
    enabled = data.get('enabled', True)
    
    if not user_identifier:
        return jsonify({'success': False, 'error': 'User identifier required'})
    
    # Find or create user
    user = NotificationUser.query.filter_by(user_identifier=user_identifier).first()
    if not user:
        user = NotificationUser(
            user_identifier=user_identifier,
            user_name=request.cookies.get('user_name', 'Anonymous'),
            notifications_enabled=enabled
        )
        db.session.add(user)
    else:
        user.notifications_enabled = enabled
    
    db.session.commit()
    return jsonify({'success': True, 'enabled': enabled})

@api_bp.route('/notifications/register-user', methods=['POST'])
def register_notification_user():
    try:
        data = request.get_json()
        user_identifier = data.get('user_identifier', '')
        user_name = data.get('user_name', 'Anonymous')
        device_info = data.get('device_info', '')
        notifications_enabled = data.get('notifications_enabled', True)
        
        if not user_identifier:
            return jsonify({'success': False, 'message': 'User identifier required'})
        
        # Find or create user
        user = NotificationUser.query.filter_by(user_identifier=user_identifier).first()
        if user:
            # Update existing user
            user.user_name = user_name
            user.device_info = device_info
            user.notifications_enabled = notifications_enabled
            user.last_seen = datetime.utcnow()
        else:
            # Create new user
            user = NotificationUser(
                user_identifier=user_identifier,
                user_name=user_name,
                device_info=device_info,
                notifications_enabled=notifications_enabled
            )
            db.session.add(user)
        
        db.session.commit()
        return jsonify({'success': True, 'message': 'User registered successfully'})
    
    except Exception as e:
        print(f"Error registering notification user: {e}")
        db.session.rollback()
        return jsonify({'success': False, 'message': str(e)}) 