#!/usr/bin/env python3
"""
Migration script to add tags column to Photo table
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
    """Add tags column to Photo table if it doesn't exist"""
    
    # Connect to the database
    db_path = 'data/wedding_photos.db'
    if not os.path.exists('data'):
        os.makedirs('data')
    
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
    
    # Commit changes
    conn.commit()
    conn.close()
    
    print("\n🎉 Database migration completed successfully!")
    return True

if __name__ == "__main__":
    print("🔄 Starting database migration...")
    success = migrate_database()
    
    if success:
        print("✅ Migration completed successfully!")
    else:
        print("❌ Migration failed!")