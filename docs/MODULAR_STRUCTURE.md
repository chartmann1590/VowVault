# Wedding Gallery - Modular Structure

This document explains the new modular structure of the Wedding Gallery application, which has been refactored from a monolithic `app.py` file into a well-organized package structure.

## Directory Structure

```
Wedding/
├── app/                          # Main application package
│   ├── __init__.py              # Application factory
│   ├── models/                  # Database models
│   │   ├── __init__.py
│   │   ├── photo.py            # Photo, Comment, Like models
│   │   ├── guestbook.py        # GuestbookEntry model
│   │   ├── messages.py         # Message, MessageComment, MessageLike models
│   │   ├── settings.py         # Settings model
│   │   ├── email.py            # EmailLog, ImmichSyncLog models
│   │   └── notifications.py    # NotificationUser, Notification models
│   ├── views/                   # Route handlers (Blueprints)
│   │   ├── __init__.py
│   │   ├── main.py             # Main routes (index, photo detail, etc.)
│   │   ├── admin.py            # Admin routes
│   │   ├── api.py              # API endpoints
│   │   ├── auth.py             # SSO authentication
│   │   ├── guestbook.py        # Guestbook routes
│   │   ├── messages.py         # Message board routes
│   │   ├── photobooth.py       # Photobooth routes
│   │   └── upload.py           # Upload routes
│   └── utils/                   # Utility functions
│       ├── __init__.py
│       ├── file_utils.py       # File handling utilities
│       ├── settings_utils.py   # Settings management
│       ├── email_utils.py      # Email processing
│       ├── immich_utils.py     # Immich sync utilities
│       └── notification_utils.py # Notification utilities
├── run.py                       # Application entry point
├── migrate_to_modular.py        # Migration script
└── check_requirements.py        # Requirements checker
```

## Key Improvements

### 1. **Separation of Concerns**
- **Models**: All database models are organized in the `app/models/` directory
- **Views**: Route handlers are separated into logical blueprints in `app/views/`
- **Utils**: Utility functions are organized by functionality in `app/utils/`

### 2. **Flask Blueprints**
The application now uses Flask Blueprints to organize routes:
- `main_bp`: Main pages (index, photo detail, privacy policy, etc.)
- `admin_bp`: Admin functionality (dashboard, settings, batch operations)
- `api_bp`: API endpoints (likes, comments, notifications)
- `auth_bp`: SSO authentication
- `guestbook_bp`: Guestbook functionality
- `messages_bp`: Message board functionality
- `photobooth_bp`: Photobooth functionality
- `upload_bp`: File upload functionality

### 3. **Application Factory Pattern**
The new `app/__init__.py` uses the application factory pattern, making it easier to:
- Create multiple instances of the app
- Configure the app for different environments
- Test the application

### 4. **Modular Utilities**
Utility functions are now organized by functionality:
- `file_utils.py`: File validation, video processing, thumbnail creation
- `settings_utils.py`: Database settings management
- `email_utils.py`: Email processing and monitoring
- `immich_utils.py`: Immich photo sync functionality
- `notification_utils.py`: Push notification handling

## Migration Process

### Step 1: Run the Migration Script
```bash
python migrate_to_modular.py
```

This script will:
- Create the new directory structure
- Backup your old `app.py` file
- Copy the database to the new location
- Create a requirements checker

### Step 2: Check Requirements
```bash
python check_requirements.py
```

### Step 3: Run the New Application
```bash
python run.py
```

## Benefits of the New Structure

### 1. **Maintainability**
- Each component has a single responsibility
- Easy to locate and modify specific functionality
- Clear separation between models, views, and utilities

### 2. **Scalability**
- Easy to add new features by creating new blueprints
- Modular structure supports team development
- Clear import structure prevents circular dependencies

### 3. **Testing**
- Each module can be tested independently
- Application factory pattern supports testing configurations
- Clear separation makes unit testing easier

### 4. **Code Organization**
- Related functionality is grouped together
- Easy to understand the application structure
- Consistent naming conventions

## File Descriptions

### Models (`app/models/`)
- **photo.py**: Photo, Comment, and Like models for the main gallery
- **guestbook.py**: GuestbookEntry model for guestbook functionality
- **messages.py**: Message, MessageComment, and MessageLike models for the message board
- **settings.py**: Settings model for application configuration
- **email.py**: EmailLog and ImmichSyncLog models for email processing
- **notifications.py**: NotificationUser and Notification models for push notifications

### Views (`app/views/`)
- **main.py**: Main application routes (index, photo detail, static files)
- **admin.py**: Admin dashboard and management functionality
- **api.py**: REST API endpoints for AJAX functionality
- **auth.py**: SSO authentication routes
- **guestbook.py**: Guestbook viewing and signing
- **messages.py**: Message board functionality
- **photobooth.py**: Virtual photobooth functionality
- **upload.py**: File upload handling

### Utils (`app/utils/`)
- **file_utils.py**: File validation, video processing, thumbnail creation
- **settings_utils.py**: Database settings management and admin access verification
- **email_utils.py**: Email processing, monitoring, and confirmation emails
- **immich_utils.py**: Immich photo sync functionality
- **notification_utils.py**: Push notification creation and management

## Configuration

The application configuration is now centralized in `app/__init__.py` using the application factory pattern. This makes it easy to:

- Configure different environments (development, production, testing)
- Override settings for different deployments
- Add new configuration options

## Database

The database models are now properly organized and imported through `app/models/__init__.py`. The database will be automatically created when you run the application for the first time.

## Running the Application

1. **Development**: `python run.py`
2. **Production**: Use a WSGI server like Gunicorn
3. **Testing**: The modular structure makes it easy to create test configurations

## Troubleshooting

### Common Issues

1. **Import Errors**: Make sure all `__init__.py` files are present
2. **Database Issues**: The database will be recreated if it doesn't exist
3. **Missing Dependencies**: Run `python check_requirements.py` to verify

### Getting Help

If you encounter issues:
1. Check that all required packages are installed
2. Verify the database file exists in `instance/wedding_photos.db`
3. Check the application logs for error messages
4. Ensure all template files are in the `templates/` directory

## Next Steps

After migrating to the modular structure:

1. **Test thoroughly**: Ensure all functionality works as expected
2. **Remove old files**: Once confirmed working, you can remove the backup `app.py`
3. **Add features**: The modular structure makes it easy to add new functionality
4. **Optimize**: Consider adding caching, database optimizations, etc.

The new modular structure provides a solid foundation for future development and maintenance of the Wedding Gallery application. 