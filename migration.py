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