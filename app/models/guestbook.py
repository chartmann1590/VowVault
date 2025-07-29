from app import db
from datetime import datetime

class GuestbookEntry(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    message = db.Column(db.Text, nullable=False)
    location = db.Column(db.String(100))
    photo_filename = db.Column(db.String(255))
    created_at = db.Column(db.DateTime, default=datetime.utcnow) 