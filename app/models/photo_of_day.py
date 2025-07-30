from app import db
from datetime import datetime, date
from sqlalchemy import UniqueConstraint

class PhotoOfDay(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    photo_id = db.Column(db.Integer, db.ForeignKey('photo.id'), nullable=False)
    date = db.Column(db.Date, nullable=False, unique=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    is_active = db.Column(db.Boolean, default=True)
    
    # Relationship to the photo
    photo = db.relationship('Photo', backref='photo_of_day_entries')
    
    # Relationship to votes
    votes = db.relationship('PhotoOfDayVote', backref='photo_of_day', lazy=True, cascade='all, delete-orphan')
    
    def __repr__(self):
        return f'<PhotoOfDay {self.date}: Photo {self.photo_id}>'
    
    @property
    def vote_count(self):
        return len(self.votes)
    
    @property
    def unique_voters(self):
        return len(set(vote.user_identifier for vote in self.votes))

class PhotoOfDayVote(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    photo_of_day_id = db.Column(db.Integer, db.ForeignKey('photo_of_day.id'), nullable=False)
    user_identifier = db.Column(db.String(100), nullable=False)
    user_name = db.Column(db.String(100), default='Anonymous')
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    # Ensure one vote per user per day
    __table_args__ = (UniqueConstraint('photo_of_day_id', 'user_identifier', name='unique_user_vote_per_day'),)
    
    def __repr__(self):
        return f'<PhotoOfDayVote {self.user_identifier} for {self.photo_of_day_id}>'

class PhotoOfDayCandidate(db.Model):
    """Model to track photos that are candidates for Photo of the Day"""
    id = db.Column(db.Integer, primary_key=True)
    photo_id = db.Column(db.Integer, db.ForeignKey('photo.id'), nullable=False)
    date_added = db.Column(db.Date, nullable=False)
    is_selected = db.Column(db.Boolean, default=False)
    selected_date = db.Column(db.Date)  # When it was selected as Photo of the Day
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    # Relationship to the photo
    photo = db.relationship('Photo', backref='photo_of_day_candidates')
    
    def __repr__(self):
        return f'<PhotoOfDayCandidate {self.photo_id} for {self.date_added}>' 