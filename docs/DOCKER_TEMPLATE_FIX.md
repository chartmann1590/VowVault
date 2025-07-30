# Docker Template Fix

## Issue Identified

When running the Docker container, the application was failing with a `TemplateNotFound: index.html` error. This was caused by incorrect Flask app configuration in the modular structure.

## Root Cause

The Flask app was created with `Flask(__name__)`, which by default looks for templates and static files in the same directory as the app package (`app/`). However, the templates and static files are located in the root directory.

## Fixes Applied

### 1. **Updated Flask App Configuration**

**File**: `app/__init__.py`

**Before**:
```python
app = Flask(__name__)
```

**After**:
```python
app = Flask(__name__, 
            template_folder='../templates',
            static_folder='../static')
```

This tells Flask to look for templates in the `../templates` directory and static files in the `../static` directory relative to the app package.

### 2. **Added Missing Database Import**

**File**: `app/views/main.py`

**Added**:
```python
from app import db
```

This was needed for the database queries in the main view.

## Testing the Fix

### 1. **Rebuild and Run Docker Container**

```bash
# Stop any running containers
docker compose down

# Rebuild the image with the fixes
docker compose build --no-cache

# Start the application
docker compose up -d

# Check logs
docker compose logs -f wedding-gallery
```

### 2. **Expected Behavior**

After the fix, you should see:
```
🚀 Starting Wedding Gallery Application...
📁 Creating upload directories...
🔄 Running database migrations...
✅ Database migration completed successfully
🌐 Starting Flask application...
 * Running on http://127.0.0.1:5000
```

And the application should be accessible at `http://localhost:5000` without template errors.

### 3. **Verify Template Loading**

The application should now be able to:
- Load the main index page (`index.html`)
- Display all templates correctly
- Serve static files properly
- Handle all routes without template errors

## Files Modified

1. **app/__init__.py**
   - Updated Flask app configuration
   - Added correct template and static folder paths

2. **app/views/main.py**
   - Added missing `from app import db` import

## Commit Information

- **Commit Hash**: `e8f1fc3`
- **Branch**: `testing`
- **Message**: "Fix template and static folder paths for Docker deployment"

## Additional Considerations

### Template Structure
The templates directory structure remains unchanged:
```
templates/
├── index.html
├── base.html
├── admin.html
├── upload.html
├── guestbook.html
├── message_board.html
├── photobooth.html
└── ... (other templates)
```

### Static Files
Static files are served from:
```
static/
├── uploads/
├── icons/
├── images/
├── manifest.json
└── sw.js
```

### Docker Volume Mounts
The Docker setup correctly mounts:
- `./uploads:/app/static/uploads` - For uploaded files
- `./data:/app/data` - For database persistence

## Troubleshooting

### If Templates Still Not Found

1. **Check Docker Build**:
   ```bash
   docker compose build --no-cache
   ```

2. **Verify File Structure**:
   ```bash
   docker compose exec wedding-gallery ls -la /app/
   docker compose exec wedding-gallery ls -la /app/templates/
   ```

3. **Check Flask Configuration**:
   ```bash
   docker compose exec wedding-gallery python -c "
   from app import create_app
   app = create_app()
   print('Template folder:', app.template_folder)
   print('Static folder:', app.static_folder)
   "
   ```

### If Database Issues Occur

1. **Check Database Path**:
   ```bash
   docker compose exec wedding-gallery ls -la /app/data/
   ```

2. **Run Migration Manually**:
   ```bash
   docker compose exec wedding-gallery python migration.py
   ```

## Next Steps

1. **Test the Application**: Verify all pages load correctly
2. **Test Upload Functionality**: Ensure file uploads work
3. **Test Admin Panel**: Verify admin functionality
4. **Test All Features**: Guestbook, messages, photobooth, etc.

## Conclusion

The template path issue has been resolved. The application should now run correctly in Docker with the modular structure. All templates and static files should be accessible and the application should function as expected. 