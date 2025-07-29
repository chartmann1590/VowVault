from app.models.settings import Settings

def get_email_settings():
    """Get email settings from database"""
    try:
        return {
            'smtp_server': Settings.get('email_smtp_server', 'smtp.gmail.com'),
            'smtp_port': Settings.get('email_smtp_port', '587'),
            'smtp_username': Settings.get('email_smtp_username', ''),
            'smtp_password': Settings.get('email_smtp_password', ''),
            'imap_server': Settings.get('email_imap_server', 'imap.gmail.com'),
            'imap_port': Settings.get('email_imap_port', '993'),
            'imap_username': Settings.get('email_imap_username', ''),
            'imap_password': Settings.get('email_imap_password', ''),
            'monitor_email': Settings.get('email_monitor_email', ''),
            'enabled': Settings.get('email_enabled', 'false').lower() == 'true'
        }
    except Exception as e:
        print(f"Error getting email settings: {e}")
        # Return default settings if database is not ready
        return {
            'smtp_server': 'smtp.gmail.com',
            'smtp_port': '587',
            'smtp_username': '',
            'smtp_password': '',
            'imap_server': 'imap.gmail.com',
            'imap_port': '993',
            'imap_username': '',
            'imap_password': '',
            'monitor_email': '',
            'enabled': False
        }

def get_immich_settings():
    """Get Immich settings from database"""
    try:
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
    except Exception as e:
        print(f"Error getting Immich settings: {e}")
        return {
            'enabled': False,
            'server_url': '',
            'api_key': '',
            'user_id': '',
            'album_name': 'Wedding Gallery',
            'sync_photos': True,
            'sync_videos': True,
            'sync_guestbook': True,
            'sync_messages': True,
            'sync_photobooth': True
        }

def get_sso_settings():
    """Get SSO settings from database"""
    try:
        return {
            'enabled': Settings.get('sso_enabled', 'false').lower() == 'true',
            'provider': Settings.get('sso_provider', 'google'),  # google, azure, okta, custom
            'client_id': Settings.get('sso_client_id', ''),
            'client_secret': Settings.get('sso_client_secret', ''),
            'authorization_url': Settings.get('sso_authorization_url', ''),
            'token_url': Settings.get('sso_token_url', ''),
            'userinfo_url': Settings.get('sso_userinfo_url', ''),
            'redirect_uri': Settings.get('sso_redirect_uri', ''),
            'scope': Settings.get('sso_scope', 'openid email profile'),
            'allowed_domains': Settings.get('sso_allowed_domains', '').split(','),
            'allowed_emails': Settings.get('sso_allowed_emails', '').split(','),
            'admin_key_fallback': Settings.get('sso_admin_key_fallback', 'true').lower() == 'true'
        }
    except Exception as e:
        print(f"Error getting SSO settings: {e}")
        return {
            'enabled': False,
            'provider': 'google',
            'client_id': '',
            'client_secret': '',
            'authorization_url': '',
            'token_url': '',
            'userinfo_url': '',
            'redirect_uri': '',
            'scope': 'openid email profile',
            'allowed_domains': [],
            'allowed_emails': [],
            'admin_key_fallback': True
        }

def verify_admin_access(admin_key=None, user_email=None, user_domain=None):
    """Verify admin access using either key-based or SSO authentication"""
    # First check if SSO is enabled
    sso_settings = get_sso_settings()
    
    if sso_settings['enabled']:
        # SSO is enabled, check if user is authenticated via SSO
        if user_email:
            # Check allowed emails
            if sso_settings['allowed_emails'] and user_email in sso_settings['allowed_emails']:
                return True
            
            # Check allowed domains
            if user_domain and sso_settings['allowed_domains']:
                for domain in sso_settings['allowed_domains']:
                    if domain.strip() and user_domain.lower().endswith(domain.strip().lower()):
                        return True
        
        # If SSO fallback is enabled, also check admin key
        if sso_settings['admin_key_fallback'] and admin_key == 'wedding2024':
            return True
            
        return False
    else:
        # SSO is disabled, use key-based authentication
        return admin_key == 'wedding2024' 