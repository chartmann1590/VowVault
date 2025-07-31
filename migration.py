#!/usr/bin/env python3
"""
Migration script to add tags column to Photo table and create Photo of the Day tables
"""

import sqlite3
import os
import sys
import hashlib
import secrets

# Add the current directory to Python path so we can import the app
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

def migrate_database():
    """Add tags column to Photo table and create Photo of the Day tables if they don't exist"""
    # Try Docker path first, then local path
    db_paths = [
        '/app/data/wedding_photos.db',  # Docker container path
        'instance/wedding_photos.db',    # Local development path
        'wedding_photos.db'              # Fallback path
    ]
    
    db_path = None
    for path in db_paths:
        if os.path.exists(path):
            db_path = path
            print(f"Using database at: {db_path}")
            break
    
    if not db_path:
        print("No database file found. It will be created when the app runs.")
        return True
    
    # Connect to database
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    
    try:
        # --- Existing migrations for Photo table and NotificationUser ---
        cursor.execute("PRAGMA table_info(photo)")
        columns = [column[1] for column in cursor.fetchall()]
        if 'tags' not in columns:
            print("Adding tags column to Photo table...")
            cursor.execute("ALTER TABLE photo ADD COLUMN tags TEXT")
            conn.commit()
            print("✅ Tags column added successfully!")
        else:
            print("✅ Tags column already exists")
        if 'uploader_identifier' not in columns:
            print("Adding uploader_identifier column to Photo table...")
            cursor.execute("ALTER TABLE photo ADD COLUMN uploader_identifier VARCHAR(100)")
            conn.commit()
            print("✅ uploader_identifier column added successfully!")
        else:
            print("✅ uploader_identifier column already exists")
        if 'media_type' not in columns:
            print("Adding media_type column to Photo table...")
            cursor.execute("ALTER TABLE photo ADD COLUMN media_type VARCHAR(10) DEFAULT 'image'")
            conn.commit()
            print("✅ media_type column added successfully!")
        else:
            print("✅ media_type column already exists")
        if 'thumbnail_filename' not in columns:
            print("Adding thumbnail_filename column to Photo table...")
            cursor.execute("ALTER TABLE photo ADD COLUMN thumbnail_filename VARCHAR(255)")
            conn.commit()
            print("✅ thumbnail_filename column added successfully!")
        else:
            print("✅ thumbnail_filename column already exists")
        if 'duration' not in columns:
            print("Adding duration column to Photo table...")
            cursor.execute("ALTER TABLE photo ADD COLUMN duration FLOAT")
            conn.commit()
            print("✅ duration column added successfully!")
        else:
            print("✅ duration column already exists")
        if 'is_photobooth' not in columns:
            print("Adding is_photobooth column to Photo table...")
            cursor.execute("ALTER TABLE photo ADD COLUMN is_photobooth BOOLEAN DEFAULT FALSE")
            conn.commit()
            print("✅ is_photobooth column added successfully!")
        else:
            print("✅ is_photobooth column already exists")
        
        # Add security-related columns to Photo table
        if 'file_hash' not in columns:
            print("Adding file_hash column to Photo table for integrity checking...")
            cursor.execute("ALTER TABLE photo ADD COLUMN file_hash VARCHAR(64)")
            conn.commit()
            print("✅ file_hash column added successfully!")
        else:
            print("✅ file_hash column already exists")
        
        if 'upload_ip' not in columns:
            print("Adding upload_ip column to Photo table for security logging...")
            cursor.execute("ALTER TABLE photo ADD COLUMN upload_ip VARCHAR(45)")
            conn.commit()
            print("✅ upload_ip column added successfully!")
        else:
            print("✅ upload_ip column already exists")
        
        if 'file_size' not in columns:
            print("Adding file_size column to Photo table...")
            cursor.execute("ALTER TABLE photo ADD COLUMN file_size INTEGER")
            conn.commit()
            print("✅ file_size column added successfully!")
        else:
            print("✅ file_size column already exists")
        
        # NotificationUser table
        cursor.execute("PRAGMA table_info(notification_user)")
        notification_user_columns = [column[1] for column in cursor.fetchall()]
        if 'push_subscription' not in notification_user_columns:
            print("Adding push_subscription column to NotificationUser table...")
            cursor.execute("ALTER TABLE notification_user ADD COLUMN push_subscription TEXT")
            conn.commit()
            print("✅ push_subscription column added successfully!")
        else:
            print("✅ push_subscription column already exists")
        if 'push_enabled' not in notification_user_columns:
            print("Adding push_enabled column to NotificationUser table...")
            cursor.execute("ALTER TABLE notification_user ADD COLUMN push_enabled BOOLEAN DEFAULT FALSE")
            conn.commit()
            print("✅ push_enabled column added successfully!")
        else:
            print("✅ push_enabled column already exists")
        if 'push_permission_granted' not in notification_user_columns:
            print("Adding push_permission_granted column to NotificationUser table...")
            cursor.execute("ALTER TABLE notification_user ADD COLUMN push_permission_granted BOOLEAN DEFAULT FALSE")
            conn.commit()
            print("✅ push_permission_granted column added successfully!")
        else:
            print("✅ push_permission_granted column already exists")
        
        # Add security-related columns to NotificationUser table
        if 'last_ip' not in notification_user_columns:
            print("Adding last_ip column to NotificationUser table for security logging...")
            cursor.execute("ALTER TABLE notification_user ADD COLUMN last_ip VARCHAR(45)")
            conn.commit()
            print("✅ last_ip column added successfully!")
        else:
            print("✅ last_ip column already exists")
        
        if 'failed_login_attempts' not in notification_user_columns:
            print("Adding failed_login_attempts column to NotificationUser table...")
            cursor.execute("ALTER TABLE notification_user ADD COLUMN failed_login_attempts INTEGER DEFAULT 0")
            conn.commit()
            print("✅ failed_login_attempts column added successfully!")
        else:
            print("✅ failed_login_attempts column already exists")
        
        if 'account_locked_until' not in notification_user_columns:
            print("Adding account_locked_until column to NotificationUser table...")
            cursor.execute("ALTER TABLE notification_user ADD COLUMN account_locked_until DATETIME")
            conn.commit()
            print("✅ account_locked_until column added successfully!")
        else:
            print("✅ account_locked_until column already exists")

        # --- Photo of the Day Tables ---
        cursor.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='photo_of_day'")
        if not cursor.fetchone():
            print("Creating photo_of_day table...")
            cursor.execute("""
                CREATE TABLE photo_of_day (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    photo_id INTEGER NOT NULL,
                    date DATE UNIQUE NOT NULL,
                    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
                    FOREIGN KEY (photo_id) REFERENCES photo (id) ON DELETE CASCADE
                )
            """)
            conn.commit()
            print("✅ photo_of_day table created successfully!")
        else:
            print("✅ photo_of_day table already exists")

        cursor.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='photo_of_day_vote'")
        if not cursor.fetchone():
            print("Creating photo_of_day_vote table...")
            cursor.execute("""
                CREATE TABLE photo_of_day_vote (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    photo_of_day_id INTEGER NOT NULL,
                    user_identifier VARCHAR(100) NOT NULL,
                    vote_type VARCHAR(10) NOT NULL CHECK (vote_type IN ('up', 'down')),
                    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
                    FOREIGN KEY (photo_of_day_id) REFERENCES photo_of_day (id) ON DELETE CASCADE,
                    UNIQUE(photo_of_day_id, user_identifier)
                )
            """)
            conn.commit()
            print("✅ photo_of_day_vote table created successfully!")
        else:
            print("✅ photo_of_day_vote table already exists")

        cursor.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='photo_of_day_candidate'")
        if not cursor.fetchone():
            print("Creating photo_of_day_candidate table...")
            cursor.execute("""
                CREATE TABLE photo_of_day_candidate (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    photo_id INTEGER NOT NULL,
                    contest_id INTEGER,
                    date_added DATE NOT NULL,
                    is_winner BOOLEAN DEFAULT FALSE,
                    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
                    FOREIGN KEY (photo_id) REFERENCES photo (id) ON DELETE CASCADE,
                    FOREIGN KEY (contest_id) REFERENCES photo_of_day_contest (id) ON DELETE CASCADE
                )
            """)
            conn.commit()
            print("✅ photo_of_day_candidate table created successfully!")
        else:
            print("✅ photo_of_day_candidate table already exists")

        # --- Photo of the Day Contest Tables ---
        cursor.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='photo_of_day_contest'")
        if not cursor.fetchone():
            print("Creating photo_of_day_contest table...")
            cursor.execute("""
                CREATE TABLE photo_of_day_contest (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    contest_date DATE UNIQUE NOT NULL,
                    is_active BOOLEAN DEFAULT TRUE,
                    voting_ends_at DATETIME,
                    winner_photo_id INTEGER,
                    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
                    FOREIGN KEY (winner_photo_id) REFERENCES photo (id) ON DELETE SET NULL
                )
            """)
            conn.commit()
            print("✅ photo_of_day_contest table created successfully!")
        else:
            print("✅ photo_of_day_contest table already exists")

        # Update photo_of_day_vote table to support new contest system
        cursor.execute("PRAGMA table_info(photo_of_day_vote)")
        columns = [column[1] for column in cursor.fetchall()]
        
        if 'contest_id' not in columns:
            print("Adding contest_id column to photo_of_day_vote table...")
            cursor.execute("ALTER TABLE photo_of_day_vote ADD COLUMN contest_id INTEGER REFERENCES photo_of_day_contest(id)")
            conn.commit()
            print("✅ contest_id column added to photo_of_day_vote table")
        
        if 'candidate_id' not in columns:
            print("Adding candidate_id column to photo_of_day_vote table...")
            cursor.execute("ALTER TABLE photo_of_day_vote ADD COLUMN candidate_id INTEGER REFERENCES photo_of_day_candidate(id)")
            conn.commit()
            print("✅ candidate_id column added to photo_of_day_vote table")

        # --- Security Audit Log Table ---
        cursor.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='security_audit_log'")
        if not cursor.fetchone():
            print("Creating security_audit_log table...")
            cursor.execute("""
                CREATE TABLE security_audit_log (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    event_type VARCHAR(50) NOT NULL,
                    user_identifier VARCHAR(100),
                    ip_address VARCHAR(45),
                    user_agent TEXT,
                    details TEXT,
                    severity VARCHAR(20) DEFAULT 'info' CHECK (severity IN ('info', 'warning', 'error', 'critical')),
                    created_at DATETIME DEFAULT CURRENT_TIMESTAMP
                )
            """)
            conn.commit()
            print("✅ security_audit_log table created successfully!")
        else:
            print("✅ security_audit_log table already exists")

        # --- Rate Limiting Table ---
        cursor.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='rate_limit'")
        if not cursor.fetchone():
            print("Creating rate_limit table...")
            cursor.execute("""
                CREATE TABLE rate_limit (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    identifier VARCHAR(100) NOT NULL,
                    endpoint VARCHAR(100) NOT NULL,
                    request_count INTEGER DEFAULT 1,
                    window_start DATETIME DEFAULT CURRENT_TIMESTAMP,
                    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
                    UNIQUE(identifier, endpoint, window_start)
                )
            """)
            conn.commit()
            print("✅ rate_limit table created successfully!")
        else:
            print("✅ rate_limit table already exists")

        # --- File Integrity Table ---
        cursor.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='file_integrity'")
        if not cursor.fetchone():
            print("Creating file_integrity table...")
            cursor.execute("""
                CREATE TABLE file_integrity (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    filename VARCHAR(255) NOT NULL,
                    file_path VARCHAR(500) NOT NULL,
                    file_hash VARCHAR(64) NOT NULL,
                    file_size INTEGER NOT NULL,
                    mime_type VARCHAR(100),
                    scan_status VARCHAR(20) DEFAULT 'pending' CHECK (scan_status IN ('pending', 'clean', 'suspicious', 'quarantined')),
                    last_verified DATETIME DEFAULT CURRENT_TIMESTAMP,
                    created_at DATETIME DEFAULT CURRENT_TIMESTAMP
                )
            """)
            conn.commit()
            print("✅ file_integrity table created successfully!")
        else:
            print("✅ file_integrity table already exists")

        # --- Slideshow Settings Table ---
        cursor.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='slideshow_settings'")
        if not cursor.fetchone():
            print("Creating slideshow_settings table...")
            cursor.execute("""
                CREATE TABLE slideshow_settings (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    key VARCHAR(100) UNIQUE NOT NULL,
                    value TEXT NOT NULL,
                    updated_at DATETIME DEFAULT CURRENT_TIMESTAMP
                )
            """)
            conn.commit()
            print("✅ slideshow_settings table created successfully!")
        else:
            print("✅ slideshow_settings table already exists")

        # --- Slideshow Activity Table ---
        cursor.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='slideshow_activity'")
        if not cursor.fetchone():
            print("Creating slideshow_activity table...")
            cursor.execute("""
                CREATE TABLE slideshow_activity (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    activity_type VARCHAR(50) NOT NULL,
                    content_id INTEGER NOT NULL,
                    content_summary TEXT,
                    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
                    is_active BOOLEAN DEFAULT TRUE
                )
            """)
            conn.commit()
            print("✅ slideshow_activity table created successfully!")
        else:
            print("✅ slideshow_activity table already exists")

        # --- SSO Settings Table ---
        cursor.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='sso_settings'")
        if not cursor.fetchone():
            print("Creating sso_settings table...")
            cursor.execute("""
                CREATE TABLE sso_settings (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    key VARCHAR(100) UNIQUE NOT NULL,
                    value TEXT NOT NULL,
                    updated_at DATETIME DEFAULT CURRENT_TIMESTAMP
                )
            """)
            conn.commit()
            print("✅ sso_settings table created successfully!")
        else:
            print("✅ sso_settings table already exists")

        # Initialize default SSO settings if they don't exist
        print("Initializing default SSO settings...")
        default_sso_settings = [
            ('sso_enabled', 'false'),
            ('sso_provider', 'google'),
            ('sso_client_id', ''),
            ('sso_client_secret', ''),
            ('sso_authorization_url', ''),
            ('sso_token_url', ''),
            ('sso_userinfo_url', ''),
            ('sso_redirect_uri', ''),
            ('sso_scope', 'openid email profile'),
            ('sso_allowed_domains', ''),
            ('sso_allowed_emails', ''),
            ('sso_admin_key_fallback', 'true')
        ]
        
        for key, value in default_sso_settings:
            cursor.execute("SELECT COUNT(*) FROM settings WHERE key = ?", (key,))
            if cursor.fetchone()[0] == 0:
                cursor.execute("INSERT INTO settings (key, value) VALUES (?, ?)", (key, value))
                print(f"✅ Initialized SSO setting: {key}")
        
        conn.commit()
        print("✅ Default SSO settings initialized successfully!")

        # --- Email Log Table ---
        cursor.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='email_log'")
        if not cursor.fetchone():
            print("Creating email_log table...")
            cursor.execute("""
                CREATE TABLE email_log (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    sender_email VARCHAR(255) NOT NULL,
                    subject VARCHAR(255),
                    received_at DATETIME DEFAULT CURRENT_TIMESTAMP,
                    processed_at DATETIME,
                    status VARCHAR(50) NOT NULL,
                    photo_count INTEGER DEFAULT 0,
                    error_message TEXT,
                    response_sent BOOLEAN DEFAULT FALSE,
                    response_type VARCHAR(50)
                )
            """)
            conn.commit()
            print("✅ email_log table created successfully!")
        else:
            print("✅ email_log table already exists")

        # --- Immich Sync Log Table ---
        cursor.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='immich_sync_log'")
        if not cursor.fetchone():
            print("Creating immich_sync_log table...")
            cursor.execute("""
                CREATE TABLE immich_sync_log (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    filename VARCHAR(255) NOT NULL,
                    file_path VARCHAR(500) NOT NULL,
                    sync_date DATETIME DEFAULT CURRENT_TIMESTAMP,
                    status VARCHAR(50) NOT NULL,
                    immich_asset_id VARCHAR(255),
                    error_message TEXT,
                    retry_count INTEGER DEFAULT 0,
                    last_retry DATETIME
                )
            """)
            conn.commit()
            print("✅ immich_sync_log table created successfully!")
        else:
            print("✅ immich_sync_log table already exists")

        # --- System Log Table ---
        cursor.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='system_log'")
        if not cursor.fetchone():
            print("Creating system_log table...")
            cursor.execute("""
                CREATE TABLE system_log (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    timestamp DATETIME DEFAULT CURRENT_TIMESTAMP,
                    level VARCHAR(20) NOT NULL,
                    category VARCHAR(50) NOT NULL,
                    message TEXT NOT NULL,
                    details TEXT,
                    user_identifier VARCHAR(100),
                    ip_address VARCHAR(45),
                    user_agent TEXT,
                    stack_trace TEXT,
                    resolved BOOLEAN DEFAULT FALSE,
                    resolved_at DATETIME,
                    resolved_by VARCHAR(100)
                )
            """)
            conn.commit()
            print("✅ system_log table created successfully!")
        else:
            print("✅ system_log table already exists")

        # Create indexes for better performance and security
        print("Creating security-related indexes...")
        
        # Index for security audit log
        cursor.execute("CREATE INDEX IF NOT EXISTS idx_security_audit_event_type ON security_audit_log(event_type)")
        cursor.execute("CREATE INDEX IF NOT EXISTS idx_security_audit_created_at ON security_audit_log(created_at)")
        cursor.execute("CREATE INDEX IF NOT EXISTS idx_security_audit_ip ON security_audit_log(ip_address)")
        
        # Index for rate limiting
        cursor.execute("CREATE INDEX IF NOT EXISTS idx_rate_limit_identifier ON rate_limit(identifier)")
        cursor.execute("CREATE INDEX IF NOT EXISTS idx_rate_limit_window ON rate_limit(window_start)")
        
        # Index for file integrity
        cursor.execute("CREATE INDEX IF NOT EXISTS idx_file_integrity_hash ON file_integrity(file_hash)")
        cursor.execute("CREATE INDEX IF NOT EXISTS idx_file_integrity_status ON file_integrity(scan_status)")
        
        # Index for photo security
        cursor.execute("CREATE INDEX IF NOT EXISTS idx_photo_upload_ip ON photo(upload_ip)")
        cursor.execute("CREATE INDEX IF NOT EXISTS idx_photo_file_hash ON photo(file_hash)")
        
        # Database optimization indexes for better performance
        print("Creating database optimization indexes...")
        
        # Photo table indexes for optimal query performance
        cursor.execute("CREATE INDEX IF NOT EXISTS idx_photo_upload_date ON photo(upload_date DESC)")
        cursor.execute("CREATE INDEX IF NOT EXISTS idx_photo_media_type ON photo(media_type)")
        cursor.execute("CREATE INDEX IF NOT EXISTS idx_photo_is_photobooth ON photo(is_photobooth)")
        cursor.execute("CREATE INDEX IF NOT EXISTS idx_photo_likes ON photo(likes DESC)")
        cursor.execute("CREATE INDEX IF NOT EXISTS idx_photo_uploader_name ON photo(uploader_name)")
        cursor.execute("CREATE INDEX IF NOT EXISTS idx_photo_description ON photo(description)")
        cursor.execute("CREATE INDEX IF NOT EXISTS idx_photo_tags ON photo(tags)")
        cursor.execute("CREATE INDEX IF NOT EXISTS idx_photo_media_upload ON photo(media_type, upload_date DESC)")
        cursor.execute("CREATE INDEX IF NOT EXISTS idx_photo_photobooth_upload ON photo(is_photobooth, upload_date DESC)")
        cursor.execute("CREATE INDEX IF NOT EXISTS idx_photo_likes_upload ON photo(likes DESC, upload_date DESC)")
        
        # Comment table indexes
        cursor.execute("CREATE INDEX IF NOT EXISTS idx_comment_photo_id ON comment(photo_id)")
        cursor.execute("CREATE INDEX IF NOT EXISTS idx_comment_created_at ON comment(created_at DESC)")
        
        # Like table indexes
        cursor.execute("CREATE INDEX IF NOT EXISTS idx_like_photo_id ON like(photo_id)")
        cursor.execute("CREATE INDEX IF NOT EXISTS idx_like_user_identifier ON like(user_identifier)")
        cursor.execute("CREATE INDEX IF NOT EXISTS idx_like_photo_user ON like(photo_id, user_identifier)")
        
        # Message table indexes
        cursor.execute("CREATE INDEX IF NOT EXISTS idx_message_created_at ON message(created_at DESC)")
        cursor.execute("CREATE INDEX IF NOT EXISTS idx_message_is_hidden ON message(is_hidden)")
        cursor.execute("CREATE INDEX IF NOT EXISTS idx_message_author ON message(author_name)")
        
        # Guestbook indexes
        cursor.execute("CREATE INDEX IF NOT EXISTS idx_guestbook_created_at ON guestbook_entry(created_at DESC)")
        cursor.execute("CREATE INDEX IF NOT EXISTS idx_guestbook_name ON guestbook_entry(name)")
        
        # Notification indexes
        cursor.execute("CREATE INDEX IF NOT EXISTS idx_notification_user_created ON notification(user_identifier, created_at DESC)")
        cursor.execute("CREATE INDEX IF NOT EXISTS idx_notification_is_read ON notification(is_read)")
        cursor.execute("CREATE INDEX IF NOT EXISTS idx_notification_type ON notification(notification_type)")
        
        # Settings indexes
        cursor.execute("CREATE INDEX IF NOT EXISTS idx_settings_key ON settings(key)")
        
        # Slideshow indexes
        cursor.execute("CREATE INDEX IF NOT EXISTS idx_slideshow_settings_key ON slideshow_settings(key)")
        cursor.execute("CREATE INDEX IF NOT EXISTS idx_slideshow_activity_type ON slideshow_activity(activity_type)")
        cursor.execute("CREATE INDEX IF NOT EXISTS idx_slideshow_activity_created ON slideshow_activity(created_at DESC)")
        cursor.execute("CREATE INDEX IF NOT EXISTS idx_slideshow_activity_active ON slideshow_activity(is_active)")
        cursor.execute("CREATE INDEX IF NOT EXISTS idx_slideshow_activity_content ON slideshow_activity(content_id)")
        
        # Log table indexes for better performance
        print("Creating log table indexes...")
        cursor.execute("CREATE INDEX IF NOT EXISTS idx_email_log_received_at ON email_log(received_at DESC)")
        cursor.execute("CREATE INDEX IF NOT EXISTS idx_email_log_status ON email_log(status)")
        cursor.execute("CREATE INDEX IF NOT EXISTS idx_email_log_sender ON email_log(sender_email)")
        
        cursor.execute("CREATE INDEX IF NOT EXISTS idx_immich_sync_log_sync_date ON immich_sync_log(sync_date DESC)")
        cursor.execute("CREATE INDEX IF NOT EXISTS idx_immich_sync_log_status ON immich_sync_log(status)")
        cursor.execute("CREATE INDEX IF NOT EXISTS idx_immich_sync_log_filename ON immich_sync_log(filename)")
        
        cursor.execute("CREATE INDEX IF NOT EXISTS idx_system_log_timestamp ON system_log(timestamp DESC)")
        cursor.execute("CREATE INDEX IF NOT EXISTS idx_system_log_level ON system_log(level)")
        cursor.execute("CREATE INDEX IF NOT EXISTS idx_system_log_category ON system_log(category)")
        cursor.execute("CREATE INDEX IF NOT EXISTS idx_system_log_resolved ON system_log(resolved)")
        cursor.execute("CREATE INDEX IF NOT EXISTS idx_system_log_user ON system_log(user_identifier)")
        cursor.execute("CREATE INDEX IF NOT EXISTS idx_system_log_ip ON system_log(ip_address)")
        
        conn.commit()
        print("✅ Database optimization indexes created successfully!")
        
        conn.commit()
        print("✅ Security indexes created successfully!")

        # Initialize timezone settings if not exists
        print("Initializing timezone settings...")
        cursor.execute("SELECT COUNT(*) FROM settings WHERE key = 'timezone_settings'")
        timezone_exists = cursor.fetchone()[0]
        
        if not timezone_exists:
            import json
            default_timezone_settings = {
                'timezone': 'UTC'
            }
            cursor.execute("INSERT INTO settings (key, value) VALUES (?, ?)", 
                         ('timezone_settings', json.dumps(default_timezone_settings)))
            print("✅ Default timezone settings initialized!")
        else:
            print("✅ Timezone settings already exist")

        # Enable WAL mode for better concurrency and data integrity
        cursor.execute("PRAGMA journal_mode=WAL")
        print("✅ WAL mode enabled for better data integrity")

        # Set secure pragmas
        cursor.execute("PRAGMA foreign_keys=ON")
        cursor.execute("PRAGMA synchronous=NORMAL")
        print("✅ Secure database pragmas configured")

        conn.commit()
        print("✅ All migrations completed successfully!")
        return True

    except Exception as e:
        print(f"❌ Error during migration: {e}")
        conn.rollback()
        return False
    finally:
        conn.close()

if __name__ == "__main__":
    success = migrate_database()
    sys.exit(0 if success else 1)