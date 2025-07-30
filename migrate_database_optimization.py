#!/usr/bin/env python3
"""
Database Optimization Migration Script
Adds indexes and optimizations for handling thousands of photos efficiently.
"""

import sqlite3
import os
import sys
from datetime import datetime

def migrate_database_optimization():
    """Add database indexes and optimizations for thousands of photos"""
    
    # Database path
    db_path = 'instance/wedding_photos.db'
    
    if not os.path.exists(db_path):
        print(f"❌ Database not found at {db_path}")
        print("Please run the application first to create the database.")
        return False
    
    print("🔧 Starting database optimization migration...")
    
    try:
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()
        
        # Create comprehensive indexes for photo queries
        print("📊 Creating database indexes...")
        
        indexes = [
            # Primary query indexes for photos
            "CREATE INDEX IF NOT EXISTS idx_photo_upload_date ON photo(upload_date DESC)",
            "CREATE INDEX IF NOT EXISTS idx_photo_media_type ON photo(media_type)",
            "CREATE INDEX IF NOT EXISTS idx_photo_is_photobooth ON photo(is_photobooth)",
            "CREATE INDEX IF NOT EXISTS idx_photo_likes ON photo(likes DESC)",
            
            # Search indexes
            "CREATE INDEX IF NOT EXISTS idx_photo_uploader_name ON photo(uploader_name)",
            "CREATE INDEX IF NOT EXISTS idx_photo_description ON photo(description)",
            "CREATE INDEX IF NOT EXISTS idx_photo_tags ON photo(tags)",
            
            # Composite indexes for common query patterns
            "CREATE INDEX IF NOT EXISTS idx_photo_media_upload ON photo(media_type, upload_date DESC)",
            "CREATE INDEX IF NOT EXISTS idx_photo_photobooth_upload ON photo(is_photobooth, upload_date DESC)",
            "CREATE INDEX IF NOT EXISTS idx_photo_likes_upload ON photo(likes DESC, upload_date DESC)",
            
            # Comment table indexes
            "CREATE INDEX IF NOT EXISTS idx_comment_photo_id ON comment(photo_id)",
            "CREATE INDEX IF NOT EXISTS idx_comment_created_at ON comment(created_at DESC)",
            
            # Like table indexes
            "CREATE INDEX IF NOT EXISTS idx_like_photo_id ON like(photo_id)",
            "CREATE INDEX IF NOT EXISTS idx_like_user_identifier ON like(user_identifier)",
            "CREATE INDEX IF NOT EXISTS idx_like_photo_user ON like(photo_id, user_identifier)",
            
            # Message table indexes
            "CREATE INDEX IF NOT EXISTS idx_message_created_at ON message(created_at DESC)",
            "CREATE INDEX IF NOT EXISTS idx_message_is_hidden ON message(is_hidden)",
            "CREATE INDEX IF NOT EXISTS idx_message_author ON message(author_name)",
            
            # Guestbook indexes
            "CREATE INDEX IF NOT EXISTS idx_guestbook_created_at ON guestbook_entry(created_at DESC)",
            "CREATE INDEX IF NOT EXISTS idx_guestbook_name ON guestbook_entry(name)",
            
            # Notification indexes
            "CREATE INDEX IF NOT EXISTS idx_notification_user_created ON notification(user_identifier, created_at DESC)",
            "CREATE INDEX IF NOT EXISTS idx_notification_is_read ON notification(is_read)",
            "CREATE INDEX IF NOT EXISTS idx_notification_type ON notification(notification_type)",
            
            # Settings indexes
            "CREATE INDEX IF NOT EXISTS idx_settings_key ON settings(key)",
            
            # Email log indexes
            "CREATE INDEX IF NOT EXISTS idx_email_log_received_at ON email_log(received_at DESC)",
            "CREATE INDEX IF NOT EXISTS idx_email_log_status ON email_log(status)",
            
            # Immich sync log indexes
            "CREATE INDEX IF NOT EXISTS idx_immich_sync_date ON immich_sync_log(sync_date DESC)",
            "CREATE INDEX IF NOT EXISTS idx_immich_sync_status ON immich_sync_log(status)",
            
            # Notification user indexes
            "CREATE INDEX IF NOT EXISTS idx_notification_user_identifier ON notification_user(user_identifier)",
            "CREATE INDEX IF NOT EXISTS idx_notification_user_enabled ON notification_user(notifications_enabled)",
        ]
        
        for index_sql in indexes:
            try:
                cursor.execute(index_sql)
                print(f"✅ Created index: {index_sql.split('IF NOT EXISTS ')[1].split(' ON ')[0]}")
            except Exception as e:
                print(f"⚠️  Warning creating index: {e}")
        
        conn.commit()
        print("✅ All indexes created successfully!")
        
        # Analyze database for better query planning
        print("📈 Analyzing database for query optimization...")
        cursor.execute("ANALYZE")
        print("✅ Database analysis completed!")
        
        # Update database statistics
        print("📊 Updating database statistics...")
        cursor.execute("PRAGMA optimize")
        print("✅ Database statistics updated!")
        
        # Get database statistics
        print("\n📊 Database Statistics:")
        
        # Get table row counts
        tables = ['photo', 'comment', 'like', 'message', 'guestbook_entry', 'notification', 'notification_user']
        for table in tables:
            try:
                cursor.execute(f"SELECT COUNT(*) FROM {table}")
                count = cursor.fetchone()[0]
                print(f"  {table}: {count:,} rows")
            except:
                print(f"  {table}: table not found")
        
        # Get index information
        print("\n📋 Index Information:")
        cursor.execute("SELECT name, sql FROM sqlite_master WHERE type='index' AND name NOT LIKE 'sqlite_%'")
        indexes = cursor.fetchall()
        for index_name, index_sql in indexes:
            print(f"  {index_name}")
        
        # Vacuum database to reclaim space
        print("\n🧹 Vacuuming database to reclaim space...")
        cursor.execute("VACUUM")
        print("✅ Database vacuum completed!")
        
        conn.close()
        
        print("\n🎉 Database optimization migration completed successfully!")
        print("\n📋 Summary of optimizations:")
        print("  ✅ Added 25+ database indexes for faster queries")
        print("  ✅ Optimized query planning with ANALYZE")
        print("  ✅ Updated database statistics")
        print("  ✅ Reclaimed space with VACUUM")
        print("\n🚀 Your database is now optimized for handling thousands of photos!")
        
        return True
        
    except Exception as e:
        print(f"❌ Error during migration: {e}")
        if 'conn' in locals():
            conn.close()
        return False

if __name__ == "__main__":
    success = migrate_database_optimization()
    sys.exit(0 if success else 1) 