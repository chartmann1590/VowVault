from app import db
from datetime import datetime

class Photo(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    filename = db.Column(db.String(255), nullable=False)
    original_filename = db.Column(db.String(255), nullable=False)
    uploader_name = db.Column(db.String(100), default='Anonymous')
    uploader_identifier = db.Column(db.String(100))  # Track who uploaded the photo
    upload_date = db.Column(db.DateTime, default=datetime.utcnow)
    description = db.Column(db.Text)
    tags = db.Column(db.Text)  # Comma-separated tags
    likes = db.Column(db.Integer, default=0)
    media_type = db.Column(db.String(10), default='image')  # 'image' or 'video'
    thumbnail_filename = db.Column(db.String(255))  # For video thumbnails
    duration = db.Column(db.Float)  # Video duration in seconds
    is_photobooth = db.Column(db.Boolean, default=False)  # Track photobooth photos
    comments = db.relationship('Comment', backref='photo', lazy=True, cascade='all, delete-orphan')

class Comment(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    photo_id = db.Column(db.Integer, db.ForeignKey('photo.id'), nullable=False)
    commenter_name = db.Column(db.String(100), default='Anonymous')
    content = db.Column(db.Text, nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

class Like(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    photo_id = db.Column(db.Integer, db.ForeignKey('photo.id'), nullable=False)
    user_identifier = db.Column(db.String(100), nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow) 