#!/usr/bin/env python3
"""
Test script to verify Docker compatibility with the new modular structure
"""

import os
import sys
import importlib

def test_imports():
    """Test that all modules can be imported"""
    print("🔍 Testing module imports...")
    
    modules_to_test = [
        'app',
        'app.models',
        'app.views',
        'app.utils',
        'app.models.photo',
        'app.models.guestbook',
        'app.models.messages',
        'app.models.settings',
        'app.models.email',
        'app.models.notifications',
        'app.views.main',
        'app.views.admin',
        'app.views.api',
        'app.views.auth',
        'app.views.guestbook',
        'app.views.messages',
        'app.views.photobooth',
        'app.views.upload',
        'app.utils.file_utils',
        'app.utils.settings_utils',
        'app.utils.email_utils',
        'app.utils.immich_utils',
        'app.utils.notification_utils'
    ]
    
    failed_imports = []
    
    for module in modules_to_test:
        try:
            importlib.import_module(module)
            print(f"✅ {module}")
        except ImportError as e:
            print(f"❌ {module}: {e}")
            failed_imports.append(module)
    
    return len(failed_imports) == 0

def test_app_factory():
    """Test that the app factory works"""
    print("\n🔍 Testing app factory...")
    
    try:
        from app import create_app
        app = create_app()
        print("✅ App factory works")
        return True
    except Exception as e:
        print(f"❌ App factory failed: {e}")
        return False

def test_database_config():
    """Test database configuration"""
    print("\n🔍 Testing database configuration...")
    
    try:
        from app import create_app
        app = create_app()
        
        # Test database URI
        db_uri = app.config['SQLALCHEMY_DATABASE_URI']
        print(f"✅ Database URI: {db_uri}")
        
        # Test upload folders
        upload_folders = [
            app.config['UPLOAD_FOLDER'],
            app.config['GUESTBOOK_UPLOAD_FOLDER'],
            app.config['MESSAGE_UPLOAD_FOLDER'],
            app.config['VIDEO_FOLDER'],
            app.config['THUMBNAIL_FOLDER'],
            app.config['PHOTOBOOTH_FOLDER'],
            app.config['BORDER_FOLDER']
        ]
        
        for folder in upload_folders:
            if os.path.exists(folder):
                print(f"✅ Upload folder exists: {folder}")
            else:
                print(f"⚠️  Upload folder missing: {folder}")
        
        return True
    except Exception as e:
        print(f"❌ Database configuration failed: {e}")
        return False

def test_blueprint_registration():
    """Test that all blueprints are registered"""
    print("\n🔍 Testing blueprint registration...")
    
    try:
        from app import create_app
        app = create_app()
        
        expected_blueprints = [
            'main',
            'admin',
            'api',
            'auth',
            'guestbook',
            'messages',
            'photobooth',
            'upload'
        ]
        
        registered_blueprints = list(app.blueprints.keys())
        
        for blueprint in expected_blueprints:
            if blueprint in registered_blueprints:
                print(f"✅ Blueprint registered: {blueprint}")
            else:
                print(f"❌ Blueprint missing: {blueprint}")
        
        return len(set(expected_blueprints) - set(registered_blueprints)) == 0
    except Exception as e:
        print(f"❌ Blueprint registration failed: {e}")
        return False

def test_docker_environment():
    """Test Docker-specific environment variables"""
    print("\n🔍 Testing Docker environment...")
    
    # Test if we're in a Docker-like environment
    docker_env_vars = [
        'DATABASE_URL',
        'FLASK_APP',
        'PYTHONUNBUFFERED'
    ]
    
    for var in docker_env_vars:
        value = os.environ.get(var)
        if value:
            print(f"✅ Environment variable set: {var}={value}")
        else:
            print(f"⚠️  Environment variable not set: {var}")
    
    # Test database paths
    db_paths = [
        '/app/data/wedding_photos.db',  # Docker path
        'instance/wedding_photos.db',    # Local path
        'wedding_photos.db'              # Fallback path
    ]
    
    for path in db_paths:
        if os.path.exists(path):
            print(f"✅ Database file exists: {path}")
            break
    else:
        print("⚠️  No database file found (will be created on first run)")
    
    return True

def main():
    """Run all tests"""
    print("🚀 Testing Docker compatibility with modular structure...\n")
    
    tests = [
        test_imports,
        test_app_factory,
        test_database_config,
        test_blueprint_registration,
        test_docker_environment
    ]
    
    passed = 0
    total = len(tests)
    
    for test in tests:
        if test():
            passed += 1
    
    print(f"\n📊 Test Results: {passed}/{total} tests passed")
    
    if passed == total:
        print("🎉 All tests passed! Docker setup is ready.")
        return 0
    else:
        print("❌ Some tests failed. Please check the errors above.")
        return 1

if __name__ == '__main__':
    sys.exit(main()) 