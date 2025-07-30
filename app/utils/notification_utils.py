from datetime import datetime
import json
import requests
from app import db
from app.models.notifications import Notification, NotificationUser

def trigger_push_notification(user_identifier, title, message, notification_type='admin'):
    """Trigger a push notification for a user"""
    try:
        # Find the user
        user = NotificationUser.query.filter_by(user_identifier=user_identifier).first()
        if not user or not user.notifications_enabled or not user.push_enabled:
            return False
        
        # Update last seen time
        user.last_seen = datetime.utcnow()
        db.session.commit()
        
        # Send push notification if subscription exists
        if user.push_subscription and user.push_permission_granted:
            return send_push_notification(user.push_subscription, title, message, notification_type)
        
        return True
    except Exception as e:
        print(f"Error triggering push notification: {e}")
        return False

def send_push_notification(subscription_json, title, message, notification_type='admin'):
    """Send a push notification using web push protocol"""
    try:
        # Parse subscription
        subscription = json.loads(subscription_json)
        
        # Prepare notification payload
        payload = {
            'title': title,
            'message': message,
            'type': notification_type,
            'timestamp': datetime.utcnow().isoformat()
        }
        
        # For now, we'll use a simple HTTP request to the subscription endpoint
        # In a production environment, you'd use a proper web push library
        # like pywebpush or implement the web push protocol
        
        headers = {
            'Content-Type': 'application/json',
            'TTL': '86400'  # 24 hours
        }
        
        # This is a simplified implementation
        # In production, you'd need to implement proper web push protocol
        # with VAPID keys and encryption
        
        print(f"Push notification would be sent to: {subscription.get('endpoint', 'No endpoint')}")
        print(f"Payload: {payload}")
        
        # For now, we'll just log that we would send the notification
        # In a real implementation, you'd use a web push library
        return True
        
    except Exception as e:
        print(f"Error sending push notification: {e}")
        return False

def create_notification_with_push(user_identifier, title, message, notification_type='admin', content_type=None, content_id=None):
    """Create a notification in the database and trigger push notification"""
    try:
        # Create notification in database
        notification = Notification(
            user_identifier=user_identifier,
            title=title,
            message=message,
            notification_type=notification_type,
            content_type=content_type,
            content_id=content_id
        )
        db.session.add(notification)
        db.session.commit()
        
        # Trigger push notification (without creating another database notification)
        trigger_push_notification(user_identifier, title, message, notification_type)
        
        return True
        
    except Exception as e:
        print(f"Error creating notification: {e}")
        db.session.rollback()
        return False 