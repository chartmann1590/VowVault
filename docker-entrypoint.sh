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

# Run database migrations
echo "🔄 Running database migrations..."
python migration.py

# Check if migration was successful
if [ $? -eq 0 ]; then
    echo "✅ Database migration completed successfully"
else
    echo "⚠️  Database migration had issues, but continuing..."
fi

# Start the Flask application
echo "🌐 Starting Flask application..."
python run.py 