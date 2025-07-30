import smtplib
import imaplib
import email
import threading
import time
from datetime import datetime
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from werkzeug.utils import secure_filename
from flask import current_app
from app import db, app
from app.models.settings import Settings
from app.models.photo import Photo
from app.models.email import EmailLog
from app.utils.settings_utils import get_email_settings
import os

def send_confirmation_email(recipient_email, photo_count, gallery_url):
    """Send confirmation email to user who uploaded photos via email"""
    try:
        email_settings = get_email_settings()
        if not email_settings['enabled'] or not email_settings['smtp_username']:
            return False
            
        msg = MIMEMultipart()
        msg['From'] = email_settings['smtp_username']
        msg['To'] = recipient_email
        msg['Subject'] = "Thank you for sharing your wedding photos!"
        
        body = f"""
        Hi there!
        
        Thank you so much for sharing your wedding photos with us! We've successfully added {photo_count} photo(s) to our wedding gallery.
        
        You can view all the photos here: {gallery_url}
        
        We're so grateful to have these memories captured from your perspective. Thank you for being part of our special day!
        
        Best wishes,
        The Happy Couple
        """
        
        msg.attach(MIMEText(body, 'plain'))
        
        # Send email
        server = smtplib.SMTP(email_settings['smtp_server'], int(email_settings['smtp_port']))
        server.starttls()
        server.login(email_settings['smtp_username'], email_settings['smtp_password'])
        server.send_message(msg)
        server.quit()
        
        return True
    except Exception as e:
        print(f"Error sending confirmation email: {e}")
        return False

def send_rejection_email(recipient_email, reason):
    """Send rejection email to user who sent non-photo content"""
    try:
        email_settings = get_email_settings()
        if not email_settings['enabled'] or not email_settings['smtp_username']:
            return False
            
        msg = MIMEMultipart()
        msg['From'] = email_settings['smtp_username']
        msg['To'] = recipient_email
        msg['Subject'] = "Photo upload - only photos accepted"
        
        body = f"""
        Hi there!
        
        Thank you for trying to share content with our wedding gallery! However, we can only accept photo attachments at this time.
        
        {reason}
        
        Please send only photo files (JPG, PNG, GIF, WebP) as attachments to this email address.
        
        Thank you for understanding!
        
        Best wishes,
        The Happy Couple
        """
        
        msg.attach(MIMEText(body, 'plain'))
        
        # Send email
        server = smtplib.SMTP(email_settings['smtp_server'], int(email_settings['smtp_port']))
        server.starttls()
        server.login(email_settings['smtp_username'], email_settings['smtp_password'])
        server.send_message(msg)
        server.quit()
        
        return True
    except Exception as e:
        print(f"Error sending rejection email: {e}")
        return False

def process_email_photos():
    """Process incoming emails and extract photos"""
    try:
        email_settings = get_email_settings()
        if not email_settings['enabled'] or not email_settings['imap_username']:
            print("Email processing skipped - not enabled or IMAP username not configured")
            return
            
        # Connect to IMAP server
        print(f"Connecting to IMAP server: {email_settings['imap_server']}:{email_settings['imap_port']}")
        mail = imaplib.IMAP4_SSL(email_settings['imap_server'], int(email_settings['imap_port']))
        mail.login(email_settings['imap_username'], email_settings['imap_password'])
        mail.select('INBOX')
        
        # Search for unread emails
        status, messages = mail.search(None, 'UNSEEN')
        
        if status != 'OK':
            print(f"IMAP search failed with status: {status}")
            return
            
        if not messages[0]:
            print("No unread emails found")
            return
            
        print(f"Found {len(messages[0].split())} unread email(s)")
            
        for num in messages[0].split():
            try:
                status, msg_data = mail.fetch(num, '(RFC822)')
                if status != 'OK':
                    continue
                    
                email_body = msg_data[0][1]
                email_message = email.message_from_bytes(email_body)
                
                sender_email = email_message['from']
                subject = email_message.get('subject', '')
                # Extract email from "Name <email@domain.com>" format
                if '<' in sender_email and '>' in sender_email:
                    sender_email = sender_email.split('<')[1].split('>')[0]
                
                photo_count = 0
                has_photos = False
                has_non_photos = False
                error_message = None
                
                # Process attachments
                for part in email_message.walk():
                    if part.get_content_maintype() == 'multipart':
                        continue
                    if part.get('Content-Disposition') is None:
                        continue
                        
                    filename = part.get_filename()
                    if filename:
                        # Check if it's a photo
                        from app.utils.file_utils import is_image
                        if is_image(filename):
                            has_photos = True
                            # Save the photo
                            file_data = part.get_payload(decode=True)
                            if file_data:
                                # Generate unique filename
                                timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
                                safe_filename = secure_filename(filename)
                                unique_filename = f"{timestamp}_{safe_filename}"
                                file_path = os.path.join(app.config['UPLOAD_FOLDER'], unique_filename)
                                
                                with open(file_path, 'wb') as f:
                                    f.write(file_data)
                                
                                # Create database entry
                                photo = Photo(
                                    filename=unique_filename,
                                    original_filename=filename,
                                    uploader_name=sender_email,
                                    upload_date=datetime.utcnow()
                                )
                                db.session.add(photo)
                                photo_count += 1
                        else:
                            has_non_photos = True
                
                # Determine status and create log entry
                if photo_count > 0:
                    status = 'success'
                    response_type = 'confirmation'
                    response_sent = True
                    
                    # Commit database changes
                    db.session.commit()
                    
                    # Send confirmation email
                    public_url = Settings.get('public_url', '')
                    if public_url:
                        send_confirmation_email(sender_email, photo_count, public_url)
                
                elif has_non_photos and not has_photos:
                    status = 'rejected'
                    response_type = 'rejection'
                    response_sent = True
                    send_rejection_email(sender_email, "We received your email but it didn't contain any photo attachments.")
                
                else:
                    status = 'rejected'
                    response_type = 'rejection'
                    response_sent = True
                    send_rejection_email(sender_email, "We received your email but it didn't contain any photo attachments.")
                
                # Create email log entry
                email_log = EmailLog(
                    sender_email=sender_email,
                    subject=subject,
                    processed_at=datetime.utcnow(),
                    status=status,
                    photo_count=photo_count,
                    response_sent=response_sent,
                    response_type=response_type
                )
                db.session.add(email_log)
                db.session.commit()
                
                # Mark email as read
                mail.store(num, '+FLAGS', '\\Seen')
                
            except Exception as e:
                print(f"Error processing email: {e}")
                # Log the error
                try:
                    email_log = EmailLog(
                        sender_email=sender_email if 'sender_email' in locals() else 'Unknown',
                        subject=subject if 'subject' in locals() else '',
                        processed_at=datetime.utcnow(),
                        status='error',
                        error_message=str(e),
                        response_sent=False
                    )
                    db.session.add(email_log)
                    db.session.commit()
                except Exception as log_error:
                    print(f"Error logging email error: {log_error}")
                continue
        
        mail.close()
        mail.logout()
        print("Email processing completed")
        
    except Exception as e:
        print(f"Error in email processing: {e}")
        # Ensure we don't leave any uncommitted database changes
        try:
            db.session.rollback()
        except Exception as rollback_error:
            print(f"Error during rollback: {rollback_error}")

def start_email_monitor():
    """Start the email monitoring thread"""
    def monitor_emails():
        from app import app
        with app.app_context():
            print("Email monitoring thread started")
            while True:
                try:
                    process_email_photos()
                    time.sleep(300)  # Check every 5 minutes
                except Exception as e:
                    print(f"Email monitor error: {e}")
                    time.sleep(600)  # Wait 10 minutes on error
    
    thread = threading.Thread(target=monitor_emails, daemon=True)
    thread.start()
    print("Email monitoring thread created") 