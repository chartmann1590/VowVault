from app import db
from app.models.email import SystemLog
from datetime import datetime
import traceback
import json
from flask import request

def log_system_event(level, category, message, details=None, user_identifier=None, ip_address=None, user_agent=None, stack_trace=None):
    """
    Log a system event to the database
    
    Args:
        level (str): 'info', 'warning', 'error', 'critical'
        category (str): 'system', 'security', 'email', 'immich', 'upload', 'database'
        message (str): The log message
        details (dict, optional): Additional details as JSON
        user_identifier (str, optional): User who triggered the event
        ip_address (str, optional): IP address of the request
        user_agent (str, optional): User agent string
        stack_trace (str, optional): Stack trace for errors
    """
    try:
        # Get request information if not provided
        if ip_address is None and request:
            ip_address = request.remote_addr
        if user_agent is None and request:
            user_agent = request.headers.get('User-Agent')
        
        # Convert details to JSON string if it's a dict
        if isinstance(details, dict):
            details = json.dumps(details, default=str)
        
        # Create the log entry
        log_entry = SystemLog(
            level=level,
            category=category,
            message=message,
            details=details,
            user_identifier=user_identifier,
            ip_address=ip_address,
            user_agent=user_agent,
            stack_trace=stack_trace
        )
        
        db.session.add(log_entry)
        db.session.commit()
        
        return log_entry
    except Exception as e:
        # Fallback to print if database logging fails
        print(f"Failed to log system event: {e}")
        print(f"Event: {level} - {category} - {message}")

def log_info(category, message, **kwargs):
    """Log an info level event"""
    return log_system_event('info', category, message, **kwargs)

def log_warning(category, message, **kwargs):
    """Log a warning level event"""
    return log_system_event('warning', category, message, **kwargs)

def log_error(category, message, **kwargs):
    """Log an error level event"""
    return log_system_event('error', category, message, **kwargs)

def log_critical(category, message, **kwargs):
    """Log a critical level event"""
    return log_system_event('critical', category, message, **kwargs)

def log_exception(category, message, exception=None, **kwargs):
    """Log an exception with stack trace"""
    if exception:
        stack_trace = traceback.format_exc()
        kwargs['stack_trace'] = stack_trace
    return log_system_event('error', category, message, **kwargs)

def log_security_event(event_type, message, **kwargs):
    """Log a security-related event"""
    return log_system_event('warning', 'security', f"{event_type}: {message}", **kwargs)

def log_upload_event(message, **kwargs):
    """Log an upload-related event"""
    return log_system_event('info', 'upload', message, **kwargs)

def log_email_event(message, **kwargs):
    """Log an email-related event"""
    return log_system_event('info', 'email', message, **kwargs)

def log_immich_event(message, **kwargs):
    """Log an Immich-related event"""
    return log_system_event('info', 'immich', message, **kwargs)

def log_database_event(message, **kwargs):
    """Log a database-related event"""
    return log_system_event('info', 'database', message, **kwargs)

def resolve_system_log(log_id, resolved_by):
    """Mark a system log as resolved"""
    try:
        log_entry = SystemLog.query.get(log_id)
        if log_entry:
            log_entry.resolved = True
            log_entry.resolved_at = datetime.utcnow()
            log_entry.resolved_by = resolved_by
            db.session.commit()
            return True
    except Exception as e:
        print(f"Failed to resolve system log: {e}")
        return False

def get_unresolved_logs(category=None):
    """Get unresolved system logs, optionally filtered by category"""
    query = SystemLog.query.filter_by(resolved=False)
    if category:
        query = query.filter_by(category=category)
    return query.order_by(SystemLog.timestamp.desc()).all()

def get_logs_by_level(level, limit=100):
    """Get logs by level"""
    return SystemLog.query.filter_by(level=level).order_by(SystemLog.timestamp.desc()).limit(limit).all()

def get_logs_by_category(category, limit=100):
    """Get logs by category"""
    return SystemLog.query.filter_by(category=category).order_by(SystemLog.timestamp.desc()).limit(limit).all() 