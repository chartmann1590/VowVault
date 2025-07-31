from app import db
from datetime import datetime

class EmailLog(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    sender_email = db.Column(db.String(255), nullable=False)
    subject = db.Column(db.String(255))
    received_at = db.Column(db.DateTime, default=datetime.utcnow)
    processed_at = db.Column(db.DateTime)
    status = db.Column(db.String(50), nullable=False)  # 'success', 'rejected', 'error'
    photo_count = db.Column(db.Integer, default=0)
    error_message = db.Column(db.Text)
    response_sent = db.Column(db.Boolean, default=False)
    response_type = db.Column(db.String(50))  # 'confirmation', 'rejection'

class ImmichSyncLog(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    filename = db.Column(db.String(255), nullable=False)
    file_path = db.Column(db.String(500), nullable=False)
    sync_date = db.Column(db.DateTime, default=datetime.utcnow)
    status = db.Column(db.String(50), nullable=False)  # 'success', 'error', 'pending'
    immich_asset_id = db.Column(db.String(255))  # Immich asset ID if successful
    error_message = db.Column(db.Text)
    retry_count = db.Column(db.Integer, default=0)
    last_retry = db.Column(db.DateTime)

class SystemLog(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    timestamp = db.Column(db.DateTime, default=datetime.utcnow)
    level = db.Column(db.String(20), nullable=False)  # 'info', 'warning', 'error', 'critical'
    category = db.Column(db.String(50), nullable=False)  # 'system', 'security', 'email', 'immich', 'upload', 'database'
    message = db.Column(db.Text, nullable=False)
    details = db.Column(db.Text)  # JSON or additional details
    user_identifier = db.Column(db.String(100))  # User who triggered the event
    ip_address = db.Column(db.String(45))  # IP address of the request
    user_agent = db.Column(db.Text)  # User agent string
    stack_trace = db.Column(db.Text)  # For errors, include stack trace
    resolved = db.Column(db.Boolean, default=False)  # Whether the issue has been resolved
    resolved_at = db.Column(db.DateTime)
    resolved_by = db.Column(db.String(100))  # Who resolved the issue 