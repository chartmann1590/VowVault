#!/bin/sh

echo "🚀 Starting Wedding Gallery Application..."

# Set environment variables for Docker
export FLASK_APP=run.py
export PYTHONUNBUFFERED=1

# Create necessary directories
echo "📁 Creating upload directories..."
mkdir -p static/uploads/guestbook
mkdir -p static/uploads/messages
mkdir -p static/uploads/videos
mkdir -p static/uploads/thumbnails
mkdir -p static/uploads/photobooth
mkdir -p static/uploads/borders

# Set secure file permissions
echo "🔒 Setting secure file permissions..."
# Set upload directories to 755 (rwxr-xr-x)
chmod 755 static/uploads
chmod 755 static/uploads/guestbook
chmod 755 static/uploads/messages
chmod 755 static/uploads/videos
chmod 755 static/uploads/thumbnails
chmod 755 static/uploads/photobooth
chmod 755 static/uploads/borders

# Set data directory permissions
if [ -d "/app/data" ]; then
    chmod 750 /app/data
    chown -R 1000:1000 /app/data
fi

# Set instance directory permissions
if [ -d "instance" ]; then
    chmod 750 instance
    chown -R 1000:1000 instance
fi

# Set secure permissions for database files
find . -name "*.db" -type f -exec chmod 640 {} \;
find . -name "*.sqlite" -type f -exec chmod 640 {} \;
find . -name "*.sqlite3" -type f -exec chmod 640 {} \;

# Set secure permissions for configuration files
find . -name "*.env" -type f -exec chmod 600 {} \;
find . -name "*.conf" -type f -exec chmod 600 {} \;

echo "✅ File permissions set securely"

# Run database migrations
echo "🔄 Running database migrations..."
python migration.py

# Check if migration was successful
if [ $? -eq 0 ]; then
    echo "✅ Database migration completed successfully"
else
    echo "⚠️  Database migration had issues, but continuing..."
fi

# Clean up old security logs (older than 30 days)
echo "🧹 Cleaning up old security logs..."
python -c "
import sys
sys.path.insert(0, '/app')
from app.utils.security_utils import SecurityUtils
from flask import Flask
app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:////app/data/wedding_photos.db'
with app.app_context():
    SecurityUtils.cleanup_old_logs(30)
"

# Start the Flask application
echo "🌐 Starting Flask application..."
python run.py 