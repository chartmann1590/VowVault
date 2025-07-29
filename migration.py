#!/usr/bin/env python3
"""
Database migration script to add navigation columns to notifications
This script runs automatically in the Docker container
"""

import sqlite3
import os

def migrate_database():
    """Add navigation columns to the notification table"""
    
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
    
    try:
        # Connect to the database
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()
        
        # Check if notification_user table exists
        cursor.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='notification_user'")
        if not cursor.fetchone():
            print("Creating notification_user table...")
            cursor.execute("""
                CREATE TABLE notification_user (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    user_identifier VARCHAR(100) UNIQUE NOT NULL,
                    user_name VARCHAR(100) DEFAULT 'Anonymous',
                    notifications_enabled BOOLEAN DEFAULT 1,
                    last_seen TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    device_info TEXT
                )
            """)
            print("✓ Created notification_user table")
        else:
            print("notification_user table already exists")
        
        # Check if notification table exists
        cursor.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='notification'")
        if not cursor.fetchone():
            print("Creating notification table...")
            cursor.execute("""
                CREATE TABLE notification (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    user_identifier VARCHAR(100) NOT NULL,
                    title VARCHAR(255) NOT NULL,
                    message TEXT NOT NULL,
                    notification_type VARCHAR(50) DEFAULT 'admin',
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    read_at TIMESTAMP,
                    is_read BOOLEAN DEFAULT 0,
                    content_type VARCHAR(50),
                    content_id INTEGER
                )
            """)
            print("✓ Created notification table with navigation columns")
        else:
            # Check if columns already exist
            cursor.execute("PRAGMA table_info(notification)")
            columns = [column[1] for column in cursor.fetchall()]
            
            print("Current notification table columns:", columns)
            
            # Add content_type column if it doesn't exist
            if 'content_type' not in columns:
                print("Adding content_type column...")
                cursor.execute("ALTER TABLE notification ADD COLUMN content_type VARCHAR(50)")
                print("✓ Added content_type column")
            else:
                print("content_type column already exists")
            
            # Add content_id column if it doesn't exist
            if 'content_id' not in columns:
                print("Adding content_id column...")
                cursor.execute("ALTER TABLE notification ADD COLUMN content_id INTEGER")
                print("✓ Added content_id column")
            else:
                print("content_id column already exists")
        
        # Commit the changes
        conn.commit()
        conn.close()
        
        print("✅ Database migration completed successfully!")
        return True
        
    except Exception as e:
        print(f"❌ Error during migration: {e}")
        return False

if __name__ == "__main__":
    print("🔄 Starting database migration...")
    success = migrate_database()
    if success:
        print("🎉 Migration completed! The notification system should now work properly.")
    else:
        print("💥 Migration failed. Please check the error messages above.")