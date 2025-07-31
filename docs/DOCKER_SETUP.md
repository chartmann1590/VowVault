# Docker Setup for Wedding Gallery

This document explains how to use Docker with the new modular structure of the Wedding Gallery application.

## Overview

The Docker setup has been updated to work with the new modular structure. All the original functionality is preserved while providing better organization and maintainability.

## Files Updated for Docker

### 1. **Dockerfile**
- Updated to copy the new `app/` directory structure
- Changed entry point to use `run.py` instead of `app.py`
- Added `curl` for health checks
- Added `libmagic1` system dependency for file type detection
- Updated to use new `docker-entrypoint.sh` script

### 2. **docker-compose.yml**
- No changes needed - works with existing configuration
- Mounts volumes for uploads and database persistence
- Includes nginx for production deployment

### 3. **docker-entrypoint.sh**
- New script that handles the modular structure
- Creates all necessary upload directories
- Runs database migrations
- Starts the Flask application

### 4. **migration.py**
- Updated to work with the new modular structure
- Added support for additional database columns
- Improved error handling

## Quick Start

### 1. **Build and Run with Docker Compose**
```bash
# Build the application
docker-compose build

# Start the services
docker-compose up -d

# Check logs
docker-compose logs -f wedding-gallery
```

### 2. **Build and Run with Docker**
```bash
# Build the image
docker build -t wedding-gallery .

# Run the container
docker run -p 5000:5000 \
  -v $(pwd)/uploads:/app/static/uploads \
  -v $(pwd)/data:/app/data \
  -e DATABASE_URL=sqlite:////app/data/wedding_photos.db \
  wedding-gallery
```

## Directory Structure in Docker

```
/app/
├── app/                          # Application package
│   ├── __init__.py              # App factory
│   ├── models/                  # Database models
│   ├── views/                   # Route blueprints
│   └── utils/                   # Utility functions
├── run.py                       # Application entry point
├── migration.py                 # Database migration script
├── docker-entrypoint.sh         # Docker startup script
├── templates/                   # HTML templates
├── static/                      # Static files
└── requirements.txt             # Python dependencies
```

## System Dependencies

The Docker container includes the following system dependencies:

- **ffmpeg**: For video processing and thumbnail generation
- **libmagic1**: For file type detection and security validation
- **gcc**: For compiling Python extensions
- **curl**: For health checks and external API calls

These dependencies are automatically installed during the Docker build process.

## Environment Variables

### Required for Docker
- `DATABASE_URL`: Database connection string (e.g., `sqlite:////app/data/wedding_photos.db`)
- `FLASK_APP`: Application entry point (`run.py`)
- `PYTHONUNBUFFERED`: Python output buffering (`1`)

### Optional
- `SECRET_KEY`: Flask secret key
- `MAIL_SERVER`: SMTP server for email functionality
- `MAIL_PORT`: SMTP port
- `MAIL_USERNAME`: SMTP username
- `MAIL_PASSWORD`: SMTP password
- `MAIL_USE_TLS`: Use TLS for email
- `MAIL_USE_SSL`: Use SSL for email

## Volume Mounts

### Uploads Directory
```yaml
volumes:
  - ./uploads:/app/static/uploads
```
This persists uploaded photos, videos, and other files across container restarts.

### Database Directory
```yaml
volumes:
  - ./data:/app/data
```
This persists the SQLite database across container restarts.

## Health Checks

The Docker Compose configuration includes health checks:

```yaml
healthcheck:
  test: ["CMD", "curl", "-f", "http://localhost:5000/"]
  interval: 30s
  timeout: 10s
  retries: 3
  start_period: 40s
```

## Database Migration

The application automatically runs database migrations on startup:

1. **Migration Script**: `migration.py` adds missing columns to the database
2. **Automatic Execution**: Runs during container startup via `docker-entrypoint.sh`
3. **Safe Migration**: Checks if columns exist before adding them

### Migration Process
```bash
# The migration runs automatically, but you can also run it manually:
docker-compose exec wedding-gallery python migration.py
```

## Production Deployment

### 1. **With Nginx (Recommended)**
```bash
# Start all services including nginx
docker-compose up -d

# The application will be available at:
# - HTTP: http://localhost
# - HTTPS: https://localhost (if SSL configured)
```

### 2. **Without Nginx (Development)**
```bash
# Start only the Flask application
docker-compose up wedding-gallery
```

## Troubleshooting

### Common Issues

#### 1. **Import Errors**
```bash
# Test the modular structure
python test-docker.py
```

#### 2. **Database Issues**
```bash
# Check database file
ls -la data/wedding_photos.db

# Run migration manually
docker-compose exec wedding-gallery python migration.py
```

#### 3. **Upload Directory Issues**
```bash
# Check upload directories
docker-compose exec wedding-gallery ls -la static/uploads/

# Create directories if missing
docker-compose exec wedding-gallery mkdir -p static/uploads/{guestbook,messages,videos,thumbnails,photobooth,borders}
```

#### 4. **Permission Issues**
```bash
# Fix permissions
sudo chown -R $USER:$USER uploads/ data/
chmod -R 755 uploads/ data/
```

### Debugging

#### 1. **Check Container Logs**
```bash
docker-compose logs wedding-gallery
```

#### 2. **Access Container Shell**
```bash
docker-compose exec wedding-gallery bash
```

#### 3. **Test Application**
```bash
# Test from inside container
docker-compose exec wedding-gallery python -c "from app import create_app; print('App works!')"
```

## Performance Optimization

### 1. **Multi-stage Build**
For production, consider using a multi-stage Dockerfile:

```dockerfile
# Build stage
FROM python:3.11-slim as builder
WORKDIR /app
COPY requirements.txt .
RUN pip install --user -r requirements.txt

# Runtime stage
FROM python:3.11-slim
WORKDIR /app
COPY --from=builder /root/.local /root/.local
COPY app/ app/
COPY run.py .
# ... rest of Dockerfile
```

### 2. **Caching**
- Requirements are copied first for better layer caching
- Static files are copied after dependencies
- Upload directories are created in the same layer

### 3. **Resource Limits**
Add to docker-compose.yml:
```yaml
services:
  wedding-gallery:
    deploy:
      resources:
        limits:
          memory: 512M
          cpus: '0.5'
```

## Security Considerations

### 1. **Non-root User**
Consider running the container as a non-root user:

```dockerfile
RUN useradd -m -u 1000 appuser
USER appuser
```

### 2. **Secrets Management**
Use Docker secrets for sensitive data:

```yaml
services:
  wedding-gallery:
    secrets:
      - db_password
      - mail_password
```

### 3. **Network Security**
Use internal networks for database connections:

```yaml
networks:
  internal:
    driver: bridge
```

## Monitoring

### 1. **Health Checks**
The application includes health check endpoints:

```bash
# Check application health
curl http://localhost:5000/

# Check admin panel (requires authentication)
curl http://localhost:5000/admin
```

### 2. **Logging**
Application logs are available via Docker:

```bash
# View logs
docker-compose logs -f wedding-gallery

# Follow logs with timestamps
docker-compose logs -f --timestamps wedding-gallery
```

## Backup and Recovery

### 1. **Database Backup**
```bash
# Backup database
docker-compose exec wedding-gallery sqlite3 /app/data/wedding_photos.db ".backup /app/backup.db"

# Copy backup from container
docker cp wedding-gallery:/app/backup.db ./backup_$(date +%Y%m%d_%H%M%S).db
```

### 2. **Uploads Backup**
```bash
# Backup uploads
tar -czf uploads_backup_$(date +%Y%m%d_%H%M%S).tar.gz uploads/
```

## Migration from Old Structure

If you're migrating from the old monolithic structure:

1. **Backup your data**:
   ```bash
   cp -r uploads/ uploads_backup/
   cp data/wedding_photos.db data/wedding_photos_backup.db
   ```

2. **Update Docker files** (already done):
   - Dockerfile updated
   - docker-compose.yml unchanged
   - New entrypoint script created

3. **Test the new structure**:
   ```bash
   python test-docker.py
   ```

4. **Deploy**:
   ```bash
   docker-compose up -d
   ```

## Timezone Support

The application includes timezone support for admin users:

### Configuration
- **Default Timezone**: UTC
- **Admin Configuration**: Accessible via `/admin/timezone-settings`
- **Global Support**: All major timezones worldwide
- **Real-time Preview**: See current time in selected timezone

### Features
- **Date/Time Display**: All admin interface dates/times shown in local timezone
- **Comprehensive List**: UTC, US, European, Asian, Australian timezones
- **Automatic Fallback**: Falls back to UTC if invalid timezone selected
- **Database Storage**: Timezone settings stored in database

### Usage
1. Access admin dashboard: `/admin?key=wedding2024`
2. Navigate to "Timezone Settings" in Settings & Configuration
3. Select your preferred timezone
4. Save settings to apply globally

## Conclusion

The Docker setup has been successfully updated to work with the new modular structure. All functionality is preserved while providing better organization, maintainability, and scalability.

The application is ready for both development and production deployment using Docker. 