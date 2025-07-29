#!/usr/bin/env python
"""
Database migration script to add video support, photobooth functionality, email processing, and Immich sync to the photo table
"""
import sqlite3
import os
import sys
from datetime import datetime

def check_column_exists(cursor, table_name, column_name):
    """Check if a column exists in a table"""
    cursor.execute(f"PRAGMA table_info({table_name})")
    columns = cursor.fetchall()
    return any(column[1] == column_name for column in columns)

def check_table_exists(cursor, table_name):
    """Check if a table exists"""
    cursor.execute("""
        SELECT name FROM sqlite_master 
        WHERE type='table' AND name=?
    """, (table_name,))
    return cursor.fetchone() is not None

def migrate_photo_table_for_videos(cursor):
    """Add video-related columns to photo table"""
    if not check_table_exists(cursor, 'photo'):
        print("Table 'photo' does not exist. Skipping photo migration.")
        return True
    
    # Add media_type column
    if not check_column_exists(cursor, 'photo', 'media_type'):
        print("Adding 'media_type' column to 'photo' table...")
        cursor.execute("""
            ALTER TABLE photo 
            ADD COLUMN media_type VARCHAR(10) DEFAULT 'image'
        """)
        print("Added 'media_type' column successfully!")
    else:
        print("Column 'media_type' already exists in 'photo' table.")
    
    # Add thumbnail_filename column
    if not check_column_exists(cursor, 'photo', 'thumbnail_filename'):
        print("Adding 'thumbnail_filename' column to 'photo' table...")
        cursor.execute("""
            ALTER TABLE photo 
            ADD COLUMN thumbnail_filename VARCHAR(255)
        """)
        print("Added 'thumbnail_filename' column successfully!")
    else:
        print("Column 'thumbnail_filename' already exists in 'photo' table.")
    
    # Add duration column
    if not check_column_exists(cursor, 'photo', 'duration'):
        print("Adding 'duration' column to 'photo' table...")
        cursor.execute("""
            ALTER TABLE photo 
            ADD COLUMN duration REAL
        """)
        print("Added 'duration' column successfully!")
    else:
        print("Column 'duration' already exists in 'photo' table.")
    
    # Add is_photobooth column
    if not check_column_exists(cursor, 'photo', 'is_photobooth'):
        print("Adding 'is_photobooth' column to 'photo' table...")
        cursor.execute("""
            ALTER TABLE photo 
            ADD COLUMN is_photobooth BOOLEAN DEFAULT 0
        """)
        print("Added 'is_photobooth' column successfully!")
    else:
        print("Column 'is_photobooth' already exists in 'photo' table.")
    
    return True

def migrate_guestbook(cursor):
    """Add photo_filename column to guestbook_entry table if it doesn't exist"""
    if not check_table_exists(cursor, 'guestbook_entry'):
        print("Table 'guestbook_entry' does not exist. Skipping guestbook migration.")
        return True
        
    if check_column_exists(cursor, 'guestbook_entry', 'photo_filename'):
        print("Column 'photo_filename' already exists in 'guestbook_entry' table.")
        return True
    
    print("Adding 'photo_filename' column to 'guestbook_entry' table...")
    cursor.execute("""
        ALTER TABLE guestbook_entry 
        ADD COLUMN photo_filename VARCHAR(255)
    """)
    print("Added 'photo_filename' column successfully!")
    return True

def create_message_tables(cursor):
    """Create message board related tables"""
    
    # Create message table
    if not check_table_exists(cursor, 'message'):
        print("Creating 'message' table...")
        cursor.execute("""
            CREATE TABLE message (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                author_name VARCHAR(100) NOT NULL DEFAULT 'Anonymous',
                content TEXT NOT NULL,
                photo_filename VARCHAR(255),
                created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
                likes INTEGER DEFAULT 0,
                is_hidden BOOLEAN DEFAULT 0
            )
        """)
        print("Created 'message' table successfully!")
    else:
        print("Table 'message' already exists.")
    
    # Create message_comment table
    if not check_table_exists(cursor, 'message_comment'):
        print("Creating 'message_comment' table...")
        cursor.execute("""
            CREATE TABLE message_comment (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                message_id INTEGER NOT NULL,
                commenter_name VARCHAR(100) DEFAULT 'Anonymous',
                content TEXT NOT NULL,
                created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
                is_hidden BOOLEAN DEFAULT 0,
                FOREIGN KEY (message_id) REFERENCES message(id) ON DELETE CASCADE
            )
        """)
        print("Created 'message_comment' table successfully!")
    else:
        print("Table 'message_comment' already exists.")
    
    # Create message_like table
    if not check_table_exists(cursor, 'message_like'):
        print("Creating 'message_like' table...")
        cursor.execute("""
            CREATE TABLE message_like (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                message_id INTEGER NOT NULL,
                user_identifier VARCHAR(100) NOT NULL,
                created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (message_id) REFERENCES message(id) ON DELETE CASCADE
            )
        """)
        print("Created 'message_like' table successfully!")
    else:
        print("Table 'message_like' already exists.")
    
    return True

def create_email_log_table(cursor):
    """Create email log table for tracking email processing"""
    
    # Create email_log table
    if not check_table_exists(cursor, 'email_log'):
        print("Creating 'email_log' table...")
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
                response_sent BOOLEAN DEFAULT 0,
                response_type VARCHAR(50)
            )
        """)
        print("Created 'email_log' table successfully!")
    else:
        print("Table 'email_log' already exists.")
    
    return True

def create_immich_sync_log_table(cursor):
    """Create Immich sync log table"""
    if check_table_exists(cursor, 'immich_sync_log'):
        print("Table 'immich_sync_log' already exists.")
        return True
    
    print("Creating 'immich_sync_log' table...")
    cursor.execute("""
        CREATE TABLE immich_sync_log (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            filename VARCHAR(255) NOT NULL,
            file_path VARCHAR(500) NOT NULL,
            sync_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            status VARCHAR(50) NOT NULL,
            immich_asset_id VARCHAR(255),
            error_message TEXT,
            retry_count INTEGER DEFAULT 0,
            last_retry TIMESTAMP
        )
    """)
    print("Table 'immich_sync_log' created successfully!")
    return True

def add_user_identifier_columns(cursor):
    """Add user identifier columns to existing tables"""
    
    # Add uploader_identifier to photo table
    if not check_column_exists(cursor, 'photo', 'uploader_identifier'):
        print("Adding 'uploader_identifier' column to 'photo' table...")
        cursor.execute("""
            ALTER TABLE photo 
            ADD COLUMN uploader_identifier VARCHAR(100)
        """)
        print("Added 'uploader_identifier' column successfully!")
    else:
        print("Column 'uploader_identifier' already exists in 'photo' table.")
    
    # Add author_identifier to message table
    if not check_column_exists(cursor, 'message', 'author_identifier'):
        print("Adding 'author_identifier' column to 'message' table...")
        cursor.execute("""
            ALTER TABLE message 
            ADD COLUMN author_identifier VARCHAR(100)
        """)
        print("Added 'author_identifier' column successfully!")
    else:
        print("Column 'author_identifier' already exists in 'message' table.")
    
    return True

def create_directories():
    """Create necessary directories for uploads"""
    directories = [
        os.path.join('static', 'uploads'),
        os.path.join('static', 'uploads', 'guestbook'),
        os.path.join('static', 'uploads', 'messages'),
        os.path.join('static', 'uploads', 'videos'),
        os.path.join('static', 'uploads', 'thumbnails'),
        os.path.join('static', 'uploads', 'photobooth'),
        os.path.join('static', 'uploads', 'borders')
    ]
    
    for directory in directories:
        if not os.path.exists(directory):
            try:
                os.makedirs(directory, exist_ok=True)
                print(f"Created directory: {directory}")
            except Exception as e:
                print(f"Error creating directory {directory}: {e}")
                return False
        else:
            print(f"Directory already exists: {directory}")
    
    return True

def migrate_database(db_path='wedding_photos.db'):
    """Run all database migrations"""
    
    # Check if database exists
    if not os.path.exists(db_path):
        print(f"Database {db_path} does not exist. It will be created when the app runs.")
        return True
    
    try:
        # Connect to database
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()
        
        # Run migrations
        success = True
        
        # Migrate photo table for video support and photobooth
        if not migrate_photo_table_for_videos(cursor):
            success = False
        
        # Migrate guestbook
        if not migrate_guestbook(cursor):
            success = False
        
        # Create message board tables
        if not create_message_tables(cursor):
            success = False
        
        # Create email log table
        if not create_email_log_table(cursor):
            success = False
        
        # Create Immich sync log table
        if not create_immich_sync_log_table(cursor):
            success = False
        
        # Add user identifier columns
        if not add_user_identifier_columns(cursor):
            success = False
        
        if success:
            # Commit changes
            conn.commit()
            print("\nAll database migrations completed successfully!")
        else:
            print("\nSome migrations failed!")
            conn.rollback()
        
        conn.close()
        return success
        
    except sqlite3.Error as e:
        print(f"Database error: {e}")
        return False
    except Exception as e:
        print(f"Unexpected error: {e}")
        return False

def main():
    """Main migration function"""
    print("=== Wedding Gallery Database Migration (with Video, Photobooth & Email Support) ===")
    print(f"Migration started at: {datetime.now()}")
    print("")
    
    # Determine database path
    db_path = os.environ.get('DATABASE_URL', 'wedding_photos.db')
    if db_path.startswith('sqlite:///'):
        db_path = db_path.replace('sqlite:///', '')
    
    # For Docker environments
    if db_path.startswith('/app/'):
        db_path = db_path.replace('/app/', '')
    
    print(f"Database path: {db_path}")
    
    # Run database migrations
    db_success = migrate_database(db_path)
    
    # Create directories
    dir_success = create_directories()
    
    if db_success and dir_success:
        print("\n✅ All migrations completed successfully!")
        return 0
    else:
        print("\n❌ Some migrations failed!")
        return 1

if __name__ == "__main__":
    sys.exit(main())