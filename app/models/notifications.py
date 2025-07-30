from app import db
from datetime import datetime

class NotificationUser(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_identifier = db.Column(db.String(100), unique=True, nullable=False)
    user_name = db.Column(db.String(100), default='Anonymous')
    notifications_enabled = db.Column(db.Boolean, default=True)
    last_seen = db.Column(db.DateTime, default=datetime.utcnow)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    device_info = db.Column(db.Text)  # Store browser/device information
    # Push notification fields
    push_subscription = db.Column(db.Text)  # JSON string of push subscription
    push_enabled = db.Column(db.Boolean, default=False)
    push_permission_granted = db.Column(db.Boolean, default=False)

class Notification(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_identifier = db.Column(db.String(100), nullable=False)
    title = db.Column(db.String(255), nullable=False)
    message = db.Column(db.Text, nullable=False)
    notification_type = db.Column(db.String(50), default='admin')  # 'admin', 'like', 'comment'
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    read_at = db.Column(db.DateTime)  # When user saw the notification
    is_read = db.Column(db.Boolean, default=False)
    # Navigation fields
    content_type = db.Column(db.String(50))  # 'photo', 'message', 'admin'
    content_id = db.Column(db.Integer)  # ID of the photo, message, etc. 