#!/usr/bin/env python
"""
Database migration script to add photo_filename column to guestbook_entry table
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

def migrate_database(db_path='wedding_photos.db'):
    """Add photo_filename column to guestbook_entry table if it doesn't exist"""
    
    # Check if database exists
    if not os.path.exists(db_path):
        print(f"Database {db_path} does not exist. No migration needed.")
        return True
    
    try:
        # Connect to database
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()
        
        # Check if guestbook_entry table exists
        cursor.execute("""
            SELECT name FROM sqlite_master 
            WHERE type='table' AND name='guestbook_entry'
        """)
        
        if not cursor.fetchone():
            print("Table 'guestbook_entry' does not exist. No migration needed.")
            conn.close()
            return True
        
        # Check if photo_filename column already exists
        if check_column_exists(cursor, 'guestbook_entry', 'photo_filename'):
            print("Column 'photo_filename' already exists in 'guestbook_entry' table.")
            conn.close()
            return True
        
        # Add photo_filename column
        print("Adding 'photo_filename' column to 'guestbook_entry' table...")
        cursor.execute("""
            ALTER TABLE guestbook_entry 
            ADD COLUMN photo_filename VARCHAR(255)
        """)
        
        # Commit changes
        conn.commit()
        print("Migration completed successfully!")
        
        # Verify the column was added
        if check_column_exists(cursor, 'guestbook_entry', 'photo_filename'):
            print("Verified: 'photo_filename' column has been added.")
        else:
            print("Error: Column was not added properly.")
            conn.close()
            return False
        
        conn.close()
        return True
        
    except sqlite3.Error as e:
        print(f"Database error: {e}")
        return False
    except Exception as e:
        print(f"Unexpected error: {e}")
        return False

def create_guestbook_upload_directory():
    """Create the guestbook upload directory if it doesn't exist"""
    guestbook_dir = os.path.join('static', 'uploads', 'guestbook')
    
    if not os.path.exists(guestbook_dir):
        try:
            os.makedirs(guestbook_dir, exist_ok=True)
            print(f"Created directory: {guestbook_dir}")
        except Exception as e:
            print(f"Error creating directory {guestbook_dir}: {e}")
            return False
    else:
        print(f"Directory already exists: {guestbook_dir}")
    
    return True

def main():
    """Main migration function"""
    print("=== Wedding Gallery Database Migration ===")
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
    
    # Run migration
    success = migrate_database(db_path)
    
    if success:
        # Create guestbook upload directory
        dir_success = create_guestbook_upload_directory()
        
        if dir_success:
            print("\n✅ Migration completed successfully!")
            return 0
        else:
            print("\n⚠️  Migration completed but directory creation failed.")
            return 1
    else:
        print("\n❌ Migration failed!")
        return 1

if __name__ == "__main__":
    sys.exit(main())