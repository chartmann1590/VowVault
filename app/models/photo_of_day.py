from app import db
from datetime import datetime, date
from sqlalchemy import UniqueConstraint

class PhotoOfDayContest(db.Model):
    """Model to represent a daily photo contest with multiple candidates"""
    id = db.Column(db.Integer, primary_key=True)
    contest_date = db.Column(db.Date, nullable=False, unique=True)
    is_active = db.Column(db.Boolean, default=True)
    voting_ends_at = db.Column(db.DateTime)  # When voting closes
    winner_photo_id = db.Column(db.Integer, db.ForeignKey('photo.id'))  # The winning photo
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    # Relationships
    candidates = db.relationship('PhotoOfDayCandidate', backref='contest', lazy=True, cascade='all, delete-orphan')
    votes = db.relationship('PhotoOfDayVote', backref='contest', lazy=True, cascade='all, delete-orphan')
    winner_photo = db.relationship('Photo', foreign_keys=[winner_photo_id])
    
    def __repr__(self):
        return f'<PhotoOfDayContest {self.contest_date}: {len(self.candidates)} candidates>'
    
    @property
    def total_votes(self):
        return len(self.votes)
    
    @property
    def unique_voters(self):
        return len(set(vote.user_identifier for vote in self.votes))
    
    @property
    def is_voting_open(self):
        if not self.voting_ends_at:
            return True  # No end time set, voting always open
        return datetime.utcnow() < self.voting_ends_at

class PhotoOfDayCandidate(db.Model):
    """Model to track photos that are candidates for Photo of the Day"""
    id = db.Column(db.Integer, primary_key=True)
    photo_id = db.Column(db.Integer, db.ForeignKey('photo.id'), nullable=False)
    contest_id = db.Column(db.Integer, db.ForeignKey('photo_of_day_contest.id'), nullable=False)
    date_added = db.Column(db.Date, nullable=False)
    is_winner = db.Column(db.Boolean, default=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    # Relationship to the photo
    photo = db.relationship('Photo', backref='photo_of_day_candidates')
    
    def __repr__(self):
        return f'<PhotoOfDayCandidate {self.photo_id} for contest {self.contest_id}>'
    
    @property
    def vote_count(self):
        return len([vote for vote in self.contest.votes if vote.candidate_id == self.id])

class PhotoOfDayVote(db.Model):
    """Model to track votes for photo of the day candidates"""
    id = db.Column(db.Integer, primary_key=True)
    contest_id = db.Column(db.Integer, db.ForeignKey('photo_of_day_contest.id'), nullable=False)
    candidate_id = db.Column(db.Integer, db.ForeignKey('photo_of_day_candidate.id'), nullable=False)
    user_identifier = db.Column(db.String(100), nullable=False)
    user_name = db.Column(db.String(100), default='Anonymous')
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    # Ensure one vote per user per contest
    __table_args__ = (UniqueConstraint('contest_id', 'user_identifier', name='unique_user_vote_per_contest'),)
    
    def __repr__(self):
        return f'<PhotoOfDayVote {self.user_identifier} for candidate {self.candidate_id}>'

# Legacy models for backward compatibility
class PhotoOfDay(db.Model):
    """Legacy model - kept for backward compatibility"""
    id = db.Column(db.Integer, primary_key=True)
    photo_id = db.Column(db.Integer, db.ForeignKey('photo.id'), nullable=False)
    date = db.Column(db.Date, nullable=False, unique=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    is_active = db.Column(db.Boolean, default=True)
    
    # Relationship to the photo
    photo = db.relationship('Photo', backref='photo_of_day_entries')
    
    def __repr__(self):
        return f'<PhotoOfDay {self.date}: Photo {self.photo_id}>'
    
    @property
    def vote_count(self):
        # Legacy model - votes are now handled by the contest system
        return 0
    
    @property
    def unique_voters(self):
        # Legacy model - votes are now handled by the contest system
        return 0 