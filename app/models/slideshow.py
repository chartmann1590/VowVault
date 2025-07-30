from app import db
from datetime import datetime

class SlideshowSettings(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    key = db.Column(db.String(100), unique=True, nullable=False)
    value = db.Column(db.Text, nullable=False)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

class SlideshowActivity(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    activity_type = db.Column(db.String(50), nullable=False)  # 'photo', 'guestbook', 'message'
    content_id = db.Column(db.Integer, nullable=False)  # ID of the photo/guestbook entry/message
    content_summary = db.Column(db.Text)  # Brief description for display
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    is_active = db.Column(db.Boolean, default=True)  # Whether to show in slideshow 