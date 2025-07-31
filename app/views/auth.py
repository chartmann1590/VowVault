from flask import Blueprint, request, redirect, url_for, session, current_app, render_template
import requests
import secrets
from urllib.parse import urlencode
from app.utils.settings_utils import get_sso_settings, verify_admin_access

auth_bp = Blueprint('auth', __name__)

@auth_bp.route('/login')
def sso_login():
    """SSO login page with enhanced security and provider support"""
    sso_settings = get_sso_settings()
    
    if not sso_settings['enabled']:
        return redirect(url_for('main.index'))
    
    # Store the intended destination
    session['next'] = request.args.get('next', url_for('admin.admin'))
    
    # Generate state parameter for security
    state = secrets.token_urlsafe(32)
    session['sso_state'] = state
    
    # Build authorization URL based on provider
    if sso_settings['provider'] == 'google':
        auth_url = 'https://accounts.google.com/oauth/authorize'
        params = {
            'client_id': sso_settings['client_id'],
            'redirect_uri': sso_settings['redirect_uri'],
            'response_type': 'code',
            'scope': sso_settings['scope'],
            'state': state,
            'access_type': 'offline',
            'prompt': 'consent'
        }
    elif sso_settings['provider'] == 'azure':
        auth_url = f"{sso_settings['authorization_url']}/oauth2/v2.0/authorize"
        params = {
            'client_id': sso_settings['client_id'],
            'redirect_uri': sso_settings['redirect_uri'],
            'response_type': 'code',
            'scope': sso_settings['scope'],
            'state': state,
            'response_mode': 'query'
        }
    elif sso_settings['provider'] == 'okta':
        auth_url = f"{sso_settings['authorization_url']}/oauth2/v1/authorize"
        params = {
            'client_id': sso_settings['client_id'],
            'redirect_uri': sso_settings['redirect_uri'],
            'response_type': 'code',
            'scope': sso_settings['scope'],
            'state': state
        }
    else:  # custom
        auth_url = sso_settings['authorization_url']
        params = {
            'client_id': sso_settings['client_id'],
            'redirect_uri': sso_settings['redirect_uri'],
            'response_type': 'code',
            'scope': sso_settings['scope'],
            'state': state
        }
    
    # Build the full authorization URL
    full_auth_url = f"{auth_url}?{urlencode(params)}"
    
    return render_template('sso_login.html', auth_url=full_auth_url, sso_settings=sso_settings)

@auth_bp.route('/callback')
def sso_callback():
    """Handle SSO callback with enhanced security and error handling"""
    sso_settings = get_sso_settings()
    
    if not sso_settings['enabled']:
        return "SSO not enabled", 400
    
    # Verify state parameter for CSRF protection
    state = request.args.get('state')
    if state != session.get('sso_state'):
        return "Invalid state parameter - possible CSRF attack", 400
    
    # Get authorization code
    code = request.args.get('code')
    if not code:
        return "No authorization code received", 400
    
    try:
        # Exchange code for access token
        token_data = {
            'client_id': sso_settings['client_id'],
            'client_secret': sso_settings['client_secret'],
            'code': code,
            'grant_type': 'authorization_code',
            'redirect_uri': sso_settings['redirect_uri']
        }
        
        # Add provider-specific token request parameters
        if sso_settings['provider'] == 'azure':
            token_data['scope'] = sso_settings['scope']
        
        token_response = requests.post(sso_settings['token_url'], data=token_data, timeout=30)
        token_response.raise_for_status()
        token_info = token_response.json()
        
        access_token = token_info.get('access_token')
        if not access_token:
            return "No access token received", 400
        
        # Get user information
        headers = {'Authorization': f"Bearer {access_token}"}
        user_response = requests.get(sso_settings['userinfo_url'], headers=headers, timeout=30)
        user_response.raise_for_status()
        user_info = user_response.json()
        
        # Extract user email and domain
        user_email = user_info.get('email', '')
        if not user_email:
            return "No email address received from SSO provider", 400
        
        user_domain = user_email.split('@')[1] if '@' in user_email else ''
        user_name = user_info.get('name', user_info.get('given_name', user_email))
        
        # Verify admin access
        if verify_admin_access(user_email=user_email, user_domain=user_domain):
            # Store user info in session
            session['sso_user_email'] = user_email
            session['sso_user_domain'] = user_domain
            session['sso_user_name'] = user_name
            
            # Clear the state parameter
            session.pop('sso_state', None)
            
            # Redirect to intended destination
            next_url = session.get('next', url_for('admin.admin'))
            session.pop('next', None)
            return redirect(next_url)
        else:
            return "Access denied. Your email is not authorized to access the admin panel.", 403
            
    except requests.exceptions.Timeout:
        return "SSO provider timeout - please try again", 500
    except requests.exceptions.RequestException as e:
        print(f"SSO callback network error: {e}")
        return "Network error during SSO authentication", 500
    except Exception as e:
        print(f"SSO callback error: {e}")
        return f"SSO authentication failed: {str(e)}", 500

@auth_bp.route('/logout')
def sso_logout():
    """SSO logout with proper session cleanup"""
    # Clear all SSO session data
    session.pop('sso_user_email', None)
    session.pop('sso_user_name', None)
    session.pop('sso_user_domain', None)
    session.pop('sso_state', None)
    session.pop('next', None)
    
    return redirect(url_for('main.index'))

@auth_bp.route('/test')
def test_sso():
    """Test SSO configuration"""
    sso_settings = get_sso_settings()
    
    if not sso_settings['enabled']:
        return "SSO is not enabled", 400
    
    # Check if required settings are configured
    required_fields = ['client_id', 'client_secret', 'redirect_uri']
    missing_fields = [field for field in required_fields if not sso_settings.get(field)]
    
    if missing_fields:
        return f"Missing required SSO settings: {', '.join(missing_fields)}", 400
    
    # Check if URLs are configured for custom provider
    if sso_settings['provider'] == 'custom':
        custom_fields = ['authorization_url', 'token_url', 'userinfo_url']
        missing_custom_fields = [field for field in custom_fields if not sso_settings.get(field)]
        if missing_custom_fields:
            return f"Missing required custom SSO URLs: {', '.join(missing_custom_fields)}", 400
    
    return "SSO configuration appears valid", 200 