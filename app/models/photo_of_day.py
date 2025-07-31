from app import db
from datetime import datetime, date
from sqlalchemy import UniqueConstraint

class PhotoOfDay(db.Model):
    """Simple Photo of the Day model - one photo per day"""
    id = db.Column(db.Integer, primary_key=True)
    photo_id = db.Column(db.Integer, db.ForeignKey('photo.id'), nullable=False)
    date = db.Column(db.Date, nullable=False, unique=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    is_active = db.Column(db.Boolean, default=True)
    
    # Relationship to the photo
    photo = db.relationship('Photo', backref='photo_of_day_entries')
    
    def __repr__(self):
        return f'<PhotoOfDay {self.date}: Photo {self.photo_id}>'

class PhotoOfDayVote(db.Model):
    """Votes for Photo of the Day"""
    id = db.Column(db.Integer, primary_key=True)
    photo_of_day_id = db.Column(db.Integer, db.ForeignKey('photo_of_day.id'), nullable=False)
    user_identifier = db.Column(db.String(100), nullable=False)
    user_name = db.Column(db.String(100), default='Anonymous')
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    # Ensure one vote per user per photo of the day
    __table_args__ = (UniqueConstraint('photo_of_day_id', 'user_identifier', name='unique_user_vote_per_day'),)
    
    def __repr__(self):
        return f'<PhotoOfDayVote {self.user_identifier} for day {self.photo_of_day_id}>'

# Legacy models for backward compatibility - these will be removed in future migrations
class PhotoOfDayContest(db.Model):
    """Legacy model - kept for backward compatibility"""
    id = db.Column(db.Integer, primary_key=True)
    contest_date = db.Column(db.Date, nullable=False, unique=True)
    is_active = db.Column(db.Boolean, default=True)
    voting_ends_at = db.Column(db.DateTime)
    winner_photo_id = db.Column(db.Integer, db.ForeignKey('photo.id'))
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    def __repr__(self):
        return f'<PhotoOfDayContest {self.contest_date}>'

class PhotoOfDayCandidate(db.Model):
    """Legacy model - kept for backward compatibility"""
    id = db.Column(db.Integer, primary_key=True)
    photo_id = db.Column(db.Integer, db.ForeignKey('photo.id'), nullable=False)
    contest_id = db.Column(db.Integer, db.ForeignKey('photo_of_day_contest.id'), nullable=False)
    date_added = db.Column(db.Date, nullable=False)
    is_winner = db.Column(db.Boolean, default=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    def __repr__(self):
        return f'<PhotoOfDayCandidate {self.photo_id}>' 