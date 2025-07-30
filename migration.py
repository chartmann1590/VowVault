#!/usr/bin/env python3
"""
Migration script to add tags column to Photo table and create Photo of the Day tables
"""

import sqlite3
import os
import sys

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

        # --- New: Photo of the Day tables ---
        # photo_of_day
        cursor.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='photo_of_day'")
        if not cursor.fetchone():
            print("Creating photo_of_day table...")
            cursor.execute("""
                CREATE TABLE photo_of_day (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    photo_id INTEGER NOT NULL,
                    date DATE NOT NULL UNIQUE,
                    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
                    is_active BOOLEAN DEFAULT TRUE,
                    FOREIGN KEY (photo_id) REFERENCES photo (id)
                )
            """)
            conn.commit()
            print("✅ photo_of_day table created successfully!")
        else:
            print("✅ photo_of_day table already exists")
        # photo_of_day_vote
        cursor.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='photo_of_day_vote'")
        if not cursor.fetchone():
            print("Creating photo_of_day_vote table...")
            cursor.execute("""
                CREATE TABLE photo_of_day_vote (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    photo_of_day_id INTEGER NOT NULL,
                    user_identifier VARCHAR(100) NOT NULL,
                    user_name VARCHAR(100) DEFAULT 'Anonymous',
                    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
                    FOREIGN KEY (photo_of_day_id) REFERENCES photo_of_day (id),
                    UNIQUE(photo_of_day_id, user_identifier)
                )
            """)
            conn.commit()
            print("✅ photo_of_day_vote table created successfully!")
        else:
            print("✅ photo_of_day_vote table already exists")
        # photo_of_day_candidate
        cursor.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='photo_of_day_candidate'")
        if not cursor.fetchone():
            print("Creating photo_of_day_candidate table...")
            cursor.execute("""
                CREATE TABLE photo_of_day_candidate (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    photo_id INTEGER NOT NULL,
                    date_added DATE NOT NULL,
                    is_selected BOOLEAN DEFAULT FALSE,
                    selected_date DATE,
                    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
                    FOREIGN KEY (photo_id) REFERENCES photo (id)
                )
            """)
            conn.commit()
            print("✅ photo_of_day_candidate table created successfully!")
        else:
            print("✅ photo_of_day_candidate table already exists")
        # Indexes
        print("Creating indexes for Photo of the Day tables...")
        cursor.execute("CREATE INDEX IF NOT EXISTS idx_photo_of_day_date ON photo_of_day(date)")
        cursor.execute("CREATE INDEX IF NOT EXISTS idx_photo_of_day_vote_user ON photo_of_day_vote(user_identifier)")
        cursor.execute("CREATE INDEX IF NOT EXISTS idx_photo_of_day_candidate_date ON photo_of_day_candidate(date_added)")
        conn.commit()
        print("✅ Indexes created successfully!")

        # --- Database Optimization Indexes ---
        print("Creating database optimization indexes...")
        
        # Photo table indexes for thousands of photos
        photo_indexes = [
            "CREATE INDEX IF NOT EXISTS idx_photo_upload_date ON photo(upload_date DESC)",
            "CREATE INDEX IF NOT EXISTS idx_photo_media_type ON photo(media_type)",
            "CREATE INDEX IF NOT EXISTS idx_photo_is_photobooth ON photo(is_photobooth)",
            "CREATE INDEX IF NOT EXISTS idx_photo_likes ON photo(likes DESC)",
            "CREATE INDEX IF NOT EXISTS idx_photo_uploader_name ON photo(uploader_name)",
            "CREATE INDEX IF NOT EXISTS idx_photo_description ON photo(description)",
            "CREATE INDEX IF NOT EXISTS idx_photo_tags ON photo(tags)",
            "CREATE INDEX IF NOT EXISTS idx_photo_media_upload ON photo(media_type, upload_date DESC)",
            "CREATE INDEX IF NOT EXISTS idx_photo_photobooth_upload ON photo(is_photobooth, upload_date DESC)",
            "CREATE INDEX IF NOT EXISTS idx_photo_likes_upload ON photo(likes DESC, upload_date DESC)"
        ]
        
        # Comment and Like table indexes
        comment_like_indexes = [
            "CREATE INDEX IF NOT EXISTS idx_comment_photo_id ON comment(photo_id)",
            "CREATE INDEX IF NOT EXISTS idx_comment_created_at ON comment(created_at DESC)",
            "CREATE INDEX IF NOT EXISTS idx_like_photo_id ON like(photo_id)",
            "CREATE INDEX IF NOT EXISTS idx_like_user_identifier ON like(user_identifier)",
            "CREATE INDEX IF NOT EXISTS idx_like_photo_user ON like(photo_id, user_identifier)"
        ]
        
        # Message and Guestbook indexes
        message_guestbook_indexes = [
            "CREATE INDEX IF NOT EXISTS idx_message_created_at ON message(created_at DESC)",
            "CREATE INDEX IF NOT EXISTS idx_message_is_hidden ON message(is_hidden)",
            "CREATE INDEX IF NOT EXISTS idx_message_author ON message(author_name)",
            "CREATE INDEX IF NOT EXISTS idx_guestbook_created_at ON guestbook_entry(created_at DESC)",
            "CREATE INDEX IF NOT EXISTS idx_guestbook_name ON guestbook_entry(name)"
        ]
        
        # Notification indexes
        notification_indexes = [
            "CREATE INDEX IF NOT EXISTS idx_notification_user_created ON notification(user_identifier, created_at DESC)",
            "CREATE INDEX IF NOT EXISTS idx_notification_is_read ON notification(is_read)",
            "CREATE INDEX IF NOT EXISTS idx_notification_type ON notification(notification_type)",
            "CREATE INDEX IF NOT EXISTS idx_notification_user_identifier ON notification_user(user_identifier)",
            "CREATE INDEX IF NOT EXISTS idx_notification_user_enabled ON notification_user(notifications_enabled)"
        ]
        
        # Settings and log indexes
        other_indexes = [
            "CREATE INDEX IF NOT EXISTS idx_settings_key ON settings(key)",
            "CREATE INDEX IF NOT EXISTS idx_email_log_received_at ON email_log(received_at DESC)",
            "CREATE INDEX IF NOT EXISTS idx_email_log_status ON email_log(status)",
            "CREATE INDEX IF NOT EXISTS idx_immich_sync_date ON immich_sync_log(sync_date DESC)",
            "CREATE INDEX IF NOT EXISTS idx_immich_sync_status ON immich_sync_log(status)"
        ]
        
        # Create all indexes
        all_indexes = photo_indexes + comment_like_indexes + message_guestbook_indexes + notification_indexes + other_indexes
        
        for index_sql in all_indexes:
            try:
                cursor.execute(index_sql)
                print(f"✅ Created index: {index_sql.split('IF NOT EXISTS ')[1].split(' ON ')[0]}")
            except Exception as e:
                print(f"⚠️  Warning creating index: {e}")
        
        conn.commit()
        print("✅ Database optimization indexes created successfully!")
        
        # Analyze database for better query planning
        print("📈 Analyzing database for query optimization...")
        cursor.execute("ANALYZE")
        print("✅ Database analysis completed!")
        
        # Update database statistics
        print("📊 Updating database statistics...")
        cursor.execute("PRAGMA optimize")
        print("✅ Database statistics updated!")

        # --- CAPTCHA Settings Migration ---
        print("🛡️ Adding CAPTCHA settings to database...")
        
        # Check if CAPTCHA settings exist, if not add them
        captcha_settings = [
            ('captcha_enabled', 'false'),
            ('captcha_upload_enabled', 'true'),
            ('captcha_guestbook_enabled', 'true'),
            ('captcha_message_enabled', 'true')
        ]
        
        for setting_key, default_value in captcha_settings:
            cursor.execute("SELECT value FROM settings WHERE key = ?", (setting_key,))
            if not cursor.fetchone():
                cursor.execute("INSERT INTO settings (key, value) VALUES (?, ?)", (setting_key, default_value))
                print(f"✅ Added CAPTCHA setting: {setting_key}")
            else:
                print(f"✅ CAPTCHA setting already exists: {setting_key}")
        
        conn.commit()
        print("✅ CAPTCHA settings migration completed!")

        # --- Slideshow Tables Migration ---
        print("🎬 Creating slideshow tables...")
        
        # Create slideshow_settings table
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS slideshow_settings (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                key VARCHAR(100) UNIQUE NOT NULL,
                value TEXT NOT NULL,
                updated_at DATETIME DEFAULT CURRENT_TIMESTAMP
            )
        """)
        
        # Create slideshow_activity table
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS slideshow_activity (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                activity_type VARCHAR(50) NOT NULL,
                content_id INTEGER NOT NULL,
                content_summary TEXT,
                created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
                is_active BOOLEAN DEFAULT TRUE
            )
        """)
        
        # Add default slideshow settings
        slideshow_settings = [
            ('slideshow_interval', '5000'),
            ('transition_effect', 'fade'),
            ('show_photos', 'true'),
            ('show_guestbook', 'true'),
            ('show_messages', 'true'),
            ('auto_refresh', 'true'),
            ('refresh_interval', '900000'),
            ('max_activities', '50'),
            ('time_range_hours', '24')
        ]
        
        for setting_key, default_value in slideshow_settings:
            cursor.execute("SELECT value FROM slideshow_settings WHERE key = ?", (setting_key,))
            if not cursor.fetchone():
                cursor.execute("INSERT INTO slideshow_settings (key, value) VALUES (?, ?)", (setting_key, default_value))
                print(f"✅ Added slideshow setting: {setting_key}")
            else:
                print(f"✅ Slideshow setting already exists: {setting_key}")
        
        # Create indexes for slideshow tables
        slideshow_indexes = [
            "CREATE INDEX IF NOT EXISTS idx_slideshow_settings_key ON slideshow_settings(key)",
            "CREATE INDEX IF NOT EXISTS idx_slideshow_activity_type ON slideshow_activity(activity_type)",
            "CREATE INDEX IF NOT EXISTS idx_slideshow_activity_created ON slideshow_activity(created_at DESC)",
            "CREATE INDEX IF NOT EXISTS idx_slideshow_activity_active ON slideshow_activity(is_active)"
        ]
        
        for index_sql in slideshow_indexes:
            try:
                cursor.execute(index_sql)
                print(f"✅ Created slideshow index: {index_sql.split('IF NOT EXISTS ')[1].split(' ON ')[0]}")
            except Exception as e:
                print(f"⚠️  Warning creating slideshow index: {e}")
        
        conn.commit()
        print("✅ Slideshow tables migration completed!")

    except Exception as e:
        print(f"❌ Error during migration: {e}")
        conn.rollback()
        return False
    finally:
        conn.close()
    return True

if __name__ == "__main__":
    print("🔄 Starting database migration...")
    success = migrate_database()
    if success:
        print("🎉 Migration completed! The search, tagging, and Photo of the Day system should now work properly.")
    else:
        print("💥 Migration failed. Please check the error messages above.")