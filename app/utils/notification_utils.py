from datetime import datetime
from app import db
from app.models.notifications import Notification, NotificationUser

def trigger_push_notification(user_identifier, title, message, notification_type='admin'):
    """Trigger a push notification for a user (without creating database notification)"""
    try:
        # Find the user
        user = NotificationUser.query.filter_by(user_identifier=user_identifier).first()
        if not user or not user.notifications_enabled:
            return False
        
        # Update last seen time
        user.last_seen = datetime.utcnow()
        db.session.commit()
        
        # In a real implementation, you would send a push notification here
        # For now, we just return True since the database notification is created separately
        return True
    except Exception as e:
        print(f"Error triggering push notification: {e}")
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