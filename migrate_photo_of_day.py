#!/usr/bin/env python3
"""
Migration script to add Photo of the Day tables
"""

import sqlite3
import os
import sys

# Add the current directory to Python path so we can import the app
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

def migrate_photo_of_day():
    """Add Photo of the Day tables to the database"""
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
        # Check if photo_of_day table exists
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
        
        # Check if photo_of_day_vote table exists
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
        
        # Check if photo_of_day_candidate table exists
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
        
        # Create indexes for better performance
        print("Creating indexes...")
        cursor.execute("CREATE INDEX IF NOT EXISTS idx_photo_of_day_date ON photo_of_day(date)")
        cursor.execute("CREATE INDEX IF NOT EXISTS idx_photo_of_day_vote_user ON photo_of_day_vote(user_identifier)")
        cursor.execute("CREATE INDEX IF NOT EXISTS idx_photo_of_day_candidate_date ON photo_of_day_candidate(date_added)")
        conn.commit()
        print("✅ Indexes created successfully!")
        
        print("\n🎉 Photo of the Day migration completed successfully!")
        return True
        
    except Exception as e:
        print(f"❌ Error during migration: {e}")
        conn.rollback()
        return False
    finally:
        conn.close()

if __name__ == "__main__":
    print("🔄 Starting Photo of the Day migration...")
    success = migrate_photo_of_day()
    if success:
        print("✅ Migration completed successfully!")
        sys.exit(0)
    else:
        print("❌ Migration failed!")
        sys.exit(1) 