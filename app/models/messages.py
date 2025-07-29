from app import db
from datetime import datetime

class Message(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    author_name = db.Column(db.String(100), nullable=False, default='Anonymous')
    author_identifier = db.Column(db.String(100))  # Track who posted the message
    content = db.Column(db.Text, nullable=False)
    photo_filename = db.Column(db.String(255))
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    likes = db.Column(db.Integer, default=0)
    is_hidden = db.Column(db.Boolean, default=False)
    message_comments = db.relationship('MessageComment', backref='message', lazy=True, cascade='all, delete-orphan')

class MessageComment(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    message_id = db.Column(db.Integer, db.ForeignKey('message.id'), nullable=False)
    commenter_name = db.Column(db.String(100), default='Anonymous')
    content = db.Column(db.Text, nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    is_hidden = db.Column(db.Boolean, default=False)

class MessageLike(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    message_id = db.Column(db.Integer, db.ForeignKey('message.id'), nullable=False)
    user_identifier = db.Column(db.String(100), nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow) 