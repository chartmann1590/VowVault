from app.models.settings import Settings
import json
from datetime import datetime

def verify_admin_access(admin_key=None, user_email=None, user_domain=None):
    """Verify admin access using either admin key or SSO credentials"""
    import os
    
    # Check if SSO is enabled and user is authenticated
    if user_email and user_domain:
        sso_settings = get_sso_settings()
        if sso_settings['enabled']:
            # Check allowed domains
            if sso_settings['allowed_domains'] and user_domain not in sso_settings['allowed_domains']:
                return False
            
            # Check allowed emails
            if sso_settings['allowed_emails'] and user_email not in sso_settings['allowed_emails']:
                return False
            
            return True
    
    # Fallback to admin key
    if admin_key:
        admin_key_from_env = os.environ.get('ADMIN_KEY', 'wedding2024')
        return admin_key == admin_key_from_env
    
    return False

def get_email_settings():
    """Get email settings from database"""
    return {
        'enabled': Settings.get('email_enabled', 'false').lower() == 'true',
        'smtp_server': Settings.get('email_smtp_server', 'smtp.gmail.com'),
        'smtp_port': Settings.get('email_smtp_port', '587'),
        'smtp_username': Settings.get('email_smtp_username', ''),
        'smtp_password': Settings.get('email_smtp_password', ''),
        'imap_server': Settings.get('email_imap_server', 'imap.gmail.com'),
        'imap_port': Settings.get('email_imap_port', '993'),
        'imap_username': Settings.get('email_imap_username', ''),
        'imap_password': Settings.get('email_imap_password', ''),
        'monitor_email': Settings.get('email_monitor_email', '')
    }

def get_immich_settings():
    """Get Immich settings from database"""
    return {
        'enabled': Settings.get('immich_enabled', 'false').lower() == 'true',
        'server_url': Settings.get('immich_server_url', ''),
        'api_key': Settings.get('immich_api_key', ''),
        'user_id': Settings.get('immich_user_id', ''),
        'album_name': Settings.get('immich_album_name', 'Wedding Gallery'),
        'sync_photos': Settings.get('immich_sync_photos', 'true').lower() == 'true',
        'sync_videos': Settings.get('immich_sync_videos', 'true').lower() == 'true',
        'sync_guestbook': Settings.get('immich_sync_guestbook', 'true').lower() == 'true',
        'sync_messages': Settings.get('immich_sync_messages', 'true').lower() == 'true',
        'sync_photobooth': Settings.get('immich_sync_photobooth', 'true').lower() == 'true'
    }

def get_sso_settings():
    """Get SSO settings from database"""
    return {
        'enabled': Settings.get('sso_enabled', 'false').lower() == 'true',
        'provider': Settings.get('sso_provider', 'google'),
        'client_id': Settings.get('sso_client_id', ''),
        'client_secret': Settings.get('sso_client_secret', ''),
        'authorization_url': Settings.get('sso_authorization_url', ''),
        'token_url': Settings.get('sso_token_url', ''),
        'userinfo_url': Settings.get('sso_userinfo_url', ''),
        'redirect_uri': Settings.get('sso_redirect_uri', ''),
        'scope': Settings.get('sso_scope', 'openid email profile'),
        'allowed_domains': Settings.get('sso_allowed_domains', '').split(',') if Settings.get('sso_allowed_domains') else [],
        'allowed_emails': Settings.get('sso_allowed_emails', '').split(',') if Settings.get('sso_allowed_emails') else [],
        'admin_key_fallback': Settings.get('sso_admin_key_fallback', 'true').lower() == 'true'
    }

def get_timezone_settings():
    """Get timezone settings from database"""
    timezone_settings = Settings.get('timezone_settings', '{}')
    return json.loads(timezone_settings) if timezone_settings else {}

def format_datetime_in_timezone(dt, format_str='%B %d, %Y at %I:%M %p'):
    """Format a datetime object in the admin's selected timezone"""
    try:
        import pytz
        
        # Get timezone settings
        timezone_settings = get_timezone_settings()
        selected_timezone = timezone_settings.get('timezone', 'UTC')
        
        # If no timezone info, assume UTC
        if dt.tzinfo is None:
            utc = pytz.UTC
            dt = utc.localize(dt)
        
        # Convert to selected timezone
        target_tz = pytz.timezone(selected_timezone)
        converted_dt = dt.astimezone(target_tz)
        
        return converted_dt.strftime(format_str)
    except Exception as e:
        # Fallback to UTC formatting if timezone conversion fails
        if dt.tzinfo is None:
            # Assume UTC if no timezone info
            pass
        return dt.strftime(format_str) 