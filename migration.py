#!/usr/bin/env python3
"""
Migration script to add tags column to Photo table and create Photo of the Day tables
"""

import sqlite3
import os
import sys
import hashlib
import secrets
from datetime import datetime

# Add the current directory to Python path so we can import the app
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

def migrate_database():
    """Add tags column to Photo table and create Photo of the Day tables if they don't exist"""
    
    # Connect to the database
    db_path = 'instance/wedding_photos.db'
    if not os.path.exists('instance'):
        os.makedirs('instance')
    
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    
    print("🔄 Starting database migration...")
    
    # --- Tags Column Migration ---
    cursor.execute("PRAGMA table_info(photo)")
    columns = [column[1] for column in cursor.fetchall()]
    
    if 'tags' not in columns:
        print("Adding tags column to Photo table...")
        cursor.execute("ALTER TABLE photo ADD COLUMN tags TEXT")
        print("✅ tags column added successfully!")
    else:
        print("✅ tags column already exists")
    
    # --- Photo of the Day Tables ---
    cursor.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='photo_of_day'")
    if not cursor.fetchone():
        print("Creating photo_of_day table...")
        cursor.execute("""
            CREATE TABLE photo_of_day (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                photo_id INTEGER NOT NULL,
                date DATE NOT NULL,
                position INTEGER DEFAULT 1,
                created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
                is_active BOOLEAN DEFAULT TRUE,
                FOREIGN KEY (photo_id) REFERENCES photo (id)
            )
        """)
        print("✅ photo_of_day table created successfully!")
    else:
        print("✅ photo_of_day table already exists")
        # Check if position column exists
        cursor.execute("PRAGMA table_info(photo_of_day)")
        columns = [column[1] for column in cursor.fetchall()]
        if 'position' not in columns:
            print("Adding position column to photo_of_day table...")
            cursor.execute("ALTER TABLE photo_of_day ADD COLUMN position INTEGER DEFAULT 1")
            print("✅ position column added successfully!")
        else:
            print("✅ position column already exists")
    
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
                FOREIGN KEY (photo_of_day_id) REFERENCES photo_of_day (id) ON DELETE CASCADE,
                UNIQUE(photo_of_day_id, user_identifier)
            )
        """)
        print("✅ photo_of_day_vote table created successfully!")
    else:
        print("✅ photo_of_day_vote table already exists")
    
    # --- Legacy Tables for Backward Compatibility ---
    cursor.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='photo_of_day_contest'")
    if not cursor.fetchone():
        print("Creating photo_of_day_contest table (legacy)...")
        cursor.execute("""
            CREATE TABLE photo_of_day_contest (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                contest_date DATE NOT NULL UNIQUE,
                is_active BOOLEAN DEFAULT TRUE,
                voting_ends_at DATETIME,
                winner_photo_id INTEGER,
                created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (winner_photo_id) REFERENCES photo (id)
            )
        """)
        print("✅ photo_of_day_contest table created successfully!")
    else:
        print("✅ photo_of_day_contest table already exists")
    
    cursor.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='photo_of_day_candidate'")
    if not cursor.fetchone():
        print("Creating photo_of_day_candidate table (legacy)...")
        cursor.execute("""
            CREATE TABLE photo_of_day_candidate (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                photo_id INTEGER NOT NULL,
                contest_id INTEGER NOT NULL,
                date_added DATE NOT NULL,
                is_winner BOOLEAN DEFAULT FALSE,
                created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (photo_id) REFERENCES photo (id),
                FOREIGN KEY (contest_id) REFERENCES photo_of_day_contest (id) ON DELETE CASCADE
            )
        """)
        print("✅ photo_of_day_candidate table created successfully!")
    else:
        print("✅ photo_of_day_candidate table already exists")
    
    # Create indexes for better performance
    cursor.execute("CREATE INDEX IF NOT EXISTS idx_photo_of_day_date ON photo_of_day(date)")
    cursor.execute("CREATE INDEX IF NOT EXISTS idx_photo_of_day_position ON photo_of_day(position)")
    cursor.execute("CREATE INDEX IF NOT EXISTS idx_photo_of_day_vote_user ON photo_of_day_vote(user_identifier)")
    cursor.execute("CREATE INDEX IF NOT EXISTS idx_photo_of_day_contest_date ON photo_of_day_contest(contest_date)")
    cursor.execute("CREATE INDEX IF NOT EXISTS idx_photo_of_day_candidate_date ON photo_of_day_candidate(date_added)")
    
    # Commit changes
    conn.commit()
    conn.close()
    
    print("\n🎉 Database migration completed successfully!")
    return True

if __name__ == "__main__":
    print("🔄 Starting Photo of the Day migration...")
    success = migrate_database()
    
    if success:
        print("✅ Migration completed successfully!")
    else:
        print("❌ Migration failed!")