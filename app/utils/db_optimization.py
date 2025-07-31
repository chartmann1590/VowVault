from app import db
from sqlalchemy import create_engine, text, Index
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import QueuePool
from flask import current_app
import sqlite3
import threading
import time
import logging
from datetime import datetime, timedelta
from functools import wraps
import json

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class DatabaseOptimizer:
    """Database optimization utilities for handling thousands of photos"""
    
    def __init__(self, app=None):
        self.app = app
        self.cache = {}
        self.cache_lock = threading.Lock()
        self.cache_ttl = 300  # 5 minutes default TTL
        
        if app is not None:
            self.init_app(app)
    
    def init_app(self, app):
        """Initialize the database optimizer with the Flask app"""
        self.app = app
        
        # Configure connection pooling
        self._configure_connection_pooling()
        
        # Create indexes on app startup
        with app.app_context():
            self.create_indexes()
    
    def _configure_connection_pooling(self):
        """Configure SQLAlchemy connection pooling for better performance"""
        if self.app.config['SQLALCHEMY_DATABASE_URI'].startswith('sqlite'):
            # For SQLite, use QueuePool with appropriate settings
            engine = create_engine(
                self.app.config['SQLALCHEMY_DATABASE_URI'],
                poolclass=QueuePool,
                pool_size=10,
                max_overflow=20,
                pool_timeout=30,
                pool_recycle=3600,
                pool_pre_ping=True
            )
            db.engine = engine
    
    def create_indexes(self):
        """Create database indexes for optimal query performance"""
        try:
            with db.engine.connect() as conn:
                # Photo table indexes
                indexes = [
                    # Primary query indexes
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
                ]
                
                for index_sql in indexes:
                    conn.execute(text(index_sql))
                
                conn.commit()
                logger.info("Database indexes created successfully")
                
        except Exception as e:
            logger.error(f"Error creating indexes: {e}")
    
    def analyze_database(self):
        """Analyze database performance and provide recommendations"""
        try:
            with db.engine.connect() as conn:
                # Get table statistics
                result = conn.execute(text("""
                    SELECT name, sql FROM sqlite_master 
                    WHERE type='table' AND name NOT LIKE 'sqlite_%'
                """))
                tables = result.fetchall()
                
                analysis = {
                    'tables': [],
                    'recommendations': [],
                    'performance_metrics': {}
                }
                
                for table_name, table_sql in tables:
                    # Get row count
                    count_result = conn.execute(text(f"SELECT COUNT(*) FROM {table_name}"))
                    row_count = count_result.fetchone()[0]
                    
                    # Get index information
                    index_result = conn.execute(text(f"PRAGMA index_list({table_name})"))
                    indexes = index_result.fetchall()
                    
                    table_info = {
                        'name': table_name,
                        'row_count': row_count,
                        'indexes': len(indexes),
                        'size_mb': self._get_table_size(table_name, conn)
                    }
                    analysis['tables'].append(table_info)
                
                # Generate recommendations
                analysis['recommendations'] = self._generate_recommendations(analysis['tables'])
                
                return analysis
                
        except Exception as e:
            logger.error(f"Error analyzing database: {e}")
            return None
    
    def _get_table_size(self, table_name, conn):
        """Get approximate table size in MB"""
        try:
            result = conn.execute(text(f"PRAGMA page_count"))
            page_count = result.fetchone()[0]
            result = conn.execute(text(f"PRAGMA page_size"))
            page_size = result.fetchone()[0]
            return (page_count * page_size) / (1024 * 1024)  # Convert to MB
        except:
            return 0
    
    def _generate_recommendations(self, tables):
        """Generate performance recommendations based on table analysis"""
        recommendations = []
        
        for table in tables:
            if table['row_count'] > 1000:
                recommendations.append(f"Table '{table['name']}' has {table['row_count']} rows - consider partitioning for better performance")
            
            if table['row_count'] > 10000:
                recommendations.append(f"Table '{table['name']}' is large ({table['row_count']} rows) - implement query result caching")
            
            if table['indexes'] < 3 and table['row_count'] > 500:
                recommendations.append(f"Table '{table['name']}' may benefit from additional indexes for better query performance")
        
        return recommendations
    
    def optimize_queries(self):
        """Run database optimization commands"""
        try:
            with db.engine.connect() as conn:
                # Analyze tables for better query planning
                conn.execute(text("ANALYZE"))
                
                # Update statistics
                conn.execute(text("PRAGMA optimize"))
                
                # Vacuum database to reclaim space
                conn.execute(text("VACUUM"))
                
                conn.commit()
                logger.info("Database optimization completed")
                return True
                
        except Exception as e:
            logger.error(f"Error optimizing database: {e}")
            return False
    
    def cache_query(self, key, query_func, ttl=None):
        """Cache query results with TTL"""
        if ttl is None:
            ttl = self.cache_ttl
        
        with self.cache_lock:
            # Check if cache entry exists and is still valid
            if key in self.cache:
                entry = self.cache[key]
                if time.time() - entry['timestamp'] < ttl:
                    return entry['data']
            
            # Execute query and cache result
            try:
                result = query_func()
                self.cache[key] = {
                    'data': result,
                    'timestamp': time.time()
                }
                return result
            except Exception as e:
                logger.error(f"Error executing cached query {key}: {e}")
                return None
    
    def clear_cache(self, key=None):
        """Clear cache entries"""
        with self.cache_lock:
            if key:
                self.cache.pop(key, None)
            else:
                self.cache.clear()
    
    def get_cache_stats(self):
        """Get cache statistics"""
        with self.cache_lock:
            return {
                'entries': len(self.cache),
                'size_mb': sum(len(str(v)) for v in self.cache.values()) / (1024 * 1024)
            }
    
    def is_enabled(self):
        """Check if database optimization is enabled"""
        return True  # Always enabled for now
    
    def get_cache_size(self):
        """Get current cache size in MB"""
        stats = self.get_cache_stats()
        return round(stats['size_mb'], 2)

# Global optimizer instance
db_optimizer = DatabaseOptimizer()

def cached_query(ttl=300):
    """Decorator for caching query results"""
    def decorator(func):
        @wraps(func)
        def wrapper(*args, **kwargs):
            # Create cache key from function name and arguments
            cache_key = f"{func.__name__}:{hash(str(args) + str(sorted(kwargs.items())))}"
            return db_optimizer.cache_query(cache_key, lambda: func(*args, **kwargs), ttl)
        return wrapper
    return decorator

def optimize_photo_queries():
    """Optimize common photo queries with eager loading and caching"""
    from app.models.photo import Photo, Comment, Like
    
    # Configure eager loading for common relationships
    Photo.comments = db.relationship('Comment', backref='photo', lazy='select', cascade='all, delete-orphan')
    Photo.likes_rel = db.relationship('Like', backref='photo', lazy='select', cascade='all, delete-orphan')
    
    return True

def get_photo_stats():
    """Get photo statistics with caching"""
    @cached_query(ttl=600)  # Cache for 10 minutes
    def _get_stats():
        from app.models.photo import Photo, Comment, Like
        
        stats = {
            'total_photos': Photo.query.count(),
            'total_videos': Photo.query.filter_by(media_type='video').count(),
            'total_photobooth': Photo.query.filter_by(is_photobooth=True).count(),
            'total_likes': db.session.query(db.func.sum(Photo.likes)).scalar() or 0,
            'total_comments': Comment.query.count(),
            'recent_uploads': Photo.query.filter(
                Photo.upload_date >= datetime.utcnow() - timedelta(days=7)
            ).count()
        }
        return stats
    
    return _get_stats()

def maintenance_task():
    """Run periodic database maintenance tasks"""
    try:
        # Optimize database
        db_optimizer.optimize_queries()
        
        # Clear old cache entries
        current_time = time.time()
        with db_optimizer.cache_lock:
            expired_keys = [
                key for key, entry in db_optimizer.cache.items()
                if current_time - entry['timestamp'] > db_optimizer.cache_ttl
            ]
            for key in expired_keys:
                del db_optimizer.cache[key]
        
        logger.info("Database maintenance completed")
        return True
        
    except Exception as e:
        logger.error(f"Error during maintenance: {e}")
        return False 