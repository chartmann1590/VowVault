from flask import Blueprint, request, redirect, url_for, session, current_app
import requests
from app.utils.settings_utils import get_sso_settings

auth_bp = Blueprint('auth', __name__)

@auth_bp.route('/login')
def sso_login():
    sso_settings = get_sso_settings()
    if not sso_settings['enabled']:
        return redirect(url_for('main.index'))
    
    # Store the intended destination
    session['next'] = request.args.get('next', url_for('admin.admin'))
    
    # Build authorization URL
    auth_params = {
        'client_id': sso_settings['client_id'],
        'redirect_uri': sso_settings['redirect_uri'],
        'response_type': 'code',
        'scope': sso_settings['scope']
    }
    
    auth_url = f"{sso_settings['authorization_url']}?{'&'.join([f'{k}={v}' for k, v in auth_params.items()])}"
    return redirect(auth_url)

@auth_bp.route('/callback')
def sso_callback():
    sso_settings = get_sso_settings()
    if not sso_settings['enabled']:
        return redirect(url_for('main.index'))
    
    # Get authorization code
    code = request.args.get('code')
    if not code:
        return "Authorization failed", 400
    
    try:
        # Exchange code for token
        token_data = {
            'client_id': sso_settings['client_id'],
            'client_secret': sso_settings['client_secret'],
            'code': code,
            'grant_type': 'authorization_code',
            'redirect_uri': sso_settings['redirect_uri']
        }
        
        token_response = requests.post(sso_settings['token_url'], data=token_data)
        token_response.raise_for_status()
        token_info = token_response.json()
        
        access_token = token_info.get('access_token')
        if not access_token:
            return "Token exchange failed", 400
        
        # Get user info
        headers = {'Authorization': f'Bearer {access_token}'}
        user_response = requests.get(sso_settings['userinfo_url'], headers=headers)
        user_response.raise_for_status()
        user_info = user_response.json()
        
        # Extract user information
        user_email = user_info.get('email', '')
        user_name = user_info.get('name', user_info.get('given_name', 'Anonymous'))
        user_domain = user_email.split('@')[1] if '@' in user_email else ''
        
        # Store in session
        session['sso_user_email'] = user_email
        session['sso_user_name'] = user_name
        session['sso_user_domain'] = user_domain
        
        # Redirect to intended destination
        next_url = session.get('next', url_for('admin.admin'))
        session.pop('next', None)
        return redirect(next_url)
        
    except Exception as e:
        print(f"SSO callback error: {e}")
        return "Authentication failed", 500

@auth_bp.route('/logout')
def sso_logout():
    # Clear session
    session.pop('sso_user_email', None)
    session.pop('sso_user_name', None)
    session.pop('sso_user_domain', None)
    return redirect(url_for('main.index')) 