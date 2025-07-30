#!/usr/bin/env python3
"""
Migration script to add tags column to Photo table
"""

import sqlite3
import os
import sys

# Add the current directory to Python path so we can import the app
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

def migrate_database():
    """Add tags column to Photo table if it doesn't exist"""
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
        # Check if tags column already exists
        cursor.execute("PRAGMA table_info(photo)")
        columns = [column[1] for column in cursor.fetchall()]
        
        if 'tags' not in columns:
            print("Adding tags column to Photo table...")
            cursor.execute("ALTER TABLE photo ADD COLUMN tags TEXT")
            conn.commit()
            print("✅ Tags column added successfully!")
        else:
            print("✅ Tags column already exists")
        
        # Check if uploader_identifier column exists
        if 'uploader_identifier' not in columns:
            print("Adding uploader_identifier column to Photo table...")
            cursor.execute("ALTER TABLE photo ADD COLUMN uploader_identifier VARCHAR(100)")
            conn.commit()
            print("✅ uploader_identifier column added successfully!")
        else:
            print("✅ uploader_identifier column already exists")
            
        # Check if media_type column exists
        if 'media_type' not in columns:
            print("Adding media_type column to Photo table...")
            cursor.execute("ALTER TABLE photo ADD COLUMN media_type VARCHAR(10) DEFAULT 'image'")
            conn.commit()
            print("✅ media_type column added successfully!")
        else:
            print("✅ media_type column already exists")
            
        # Check if thumbnail_filename column exists
        if 'thumbnail_filename' not in columns:
            print("Adding thumbnail_filename column to Photo table...")
            cursor.execute("ALTER TABLE photo ADD COLUMN thumbnail_filename VARCHAR(255)")
            conn.commit()
            print("✅ thumbnail_filename column added successfully!")
        else:
            print("✅ thumbnail_filename column already exists")
            
        # Check if duration column exists
        if 'duration' not in columns:
            print("Adding duration column to Photo table...")
            cursor.execute("ALTER TABLE photo ADD COLUMN duration FLOAT")
            conn.commit()
            print("✅ duration column added successfully!")
        else:
            print("✅ duration column already exists")
            
        # Check if is_photobooth column exists
        if 'is_photobooth' not in columns:
            print("Adding is_photobooth column to Photo table...")
            cursor.execute("ALTER TABLE photo ADD COLUMN is_photobooth BOOLEAN DEFAULT FALSE")
            conn.commit()
            print("✅ is_photobooth column added successfully!")
        else:
            print("✅ is_photobooth column already exists")
            
        # Check NotificationUser table for push notification fields
        cursor.execute("PRAGMA table_info(notification_user)")
        notification_user_columns = [column[1] for column in cursor.fetchall()]
        
        # Check if push_subscription column exists
        if 'push_subscription' not in notification_user_columns:
            print("Adding push_subscription column to NotificationUser table...")
            cursor.execute("ALTER TABLE notification_user ADD COLUMN push_subscription TEXT")
            conn.commit()
            print("✅ push_subscription column added successfully!")
        else:
            print("✅ push_subscription column already exists")
            
        # Check if push_enabled column exists
        if 'push_enabled' not in notification_user_columns:
            print("Adding push_enabled column to NotificationUser table...")
            cursor.execute("ALTER TABLE notification_user ADD COLUMN push_enabled BOOLEAN DEFAULT FALSE")
            conn.commit()
            print("✅ push_enabled column added successfully!")
        else:
            print("✅ push_enabled column already exists")
            
        # Check if push_permission_granted column exists
        if 'push_permission_granted' not in notification_user_columns:
            print("Adding push_permission_granted column to NotificationUser table...")
            cursor.execute("ALTER TABLE notification_user ADD COLUMN push_permission_granted BOOLEAN DEFAULT FALSE")
            conn.commit()
            print("✅ push_permission_granted column added successfully!")
        else:
            print("✅ push_permission_granted column already exists")
            
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
        print("🎉 Migration completed! The search and tagging system should now work properly.")
    else:
        print("💥 Migration failed. Please check the error messages above.")