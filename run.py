from app import create_app, db
from app.models import *
from app.utils.email_utils import start_email_monitor, get_email_settings
from app.utils.system_logger import log_info, log_error, log_exception

app = create_app()

if __name__ == '__main__':
    with app.app_context():
        db.create_all()
        
        # Log application startup
        try:
            log_info('system', 'Application started successfully')
        except Exception as e:
            print(f"Failed to log application startup: {e}")
        
        # Start email monitor if enabled
        try:
            email_settings = get_email_settings()
            print(f"Email settings - Enabled: {email_settings['enabled']}, IMAP Username: {email_settings['imap_username']}, IMAP Password: {'*' * len(email_settings['imap_password']) if email_settings['imap_password'] else 'Not set'}")
            
            if email_settings['enabled'] and email_settings['imap_username'] and email_settings['imap_password']:
                start_email_monitor()
                print("Email monitor started successfully")
                log_info('email', 'Email monitor started successfully')
            else:
                print("Email monitor not started - not enabled or not configured")
                log_info('email', 'Email monitor not started - not enabled or not configured')
                if not email_settings['enabled']:
                    print("  - Email monitoring is disabled")
                if not email_settings['imap_username']:
                    print("  - IMAP username not configured")
                if not email_settings['imap_password']:
                    print("  - IMAP password not configured")
        except Exception as e:
            print(f"Email monitor not started: {e}")
            log_error('email', f'Email monitor failed to start: {e}')
            
    app.run(debug=True, host='0.0.0.0', port=5000) 