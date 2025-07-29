#!/usr/bin/env python3
"""
Migration script to add tags column to Photo table
"""

import sqlite3
import os

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