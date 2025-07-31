# 💑 VowVault - Wedding Photo Gallery

A beautiful, self-hosted wedding photo gallery application that allows wedding guests to upload and share photos without requiring any login. Built with Flask and designed with love for your special day.

![Python](https://img.shields.io/badge/python-3.11-blue.svg)
![Flask](https://img.shields.io/badge/flask-3.0-green.svg)
![Docker](https://img.shields.io/badge/docker-ready-blue.svg)
![License](https://img.shields.io/badge/license-MIT-green.svg)
![Security](https://img.shields.io/badge/security-enhanced-red.svg)

## 📋 Table of Contents

### 🚀 Getting Started
- [✨ Features](docs/features.md) - Complete feature overview for guests and admins
- [🚀 Installation Guide](docs/installation.md) - Quick start and production deployment
- [📱 Usage Guide](docs/usage.md) - Step-by-step instructions for guests and admins
- [📱 Progressive Web App](docs/pwa.md) - PWA installation and troubleshooting

### 🔒 Security & Privacy
- [🔒 Security Guide](docs/SECURITY.md) - Comprehensive security features and best practices
- [🛡️ Privacy Protection](docs/SECURITY.md#-privacy-protection) - Data minimization and retention policies
- [🚨 Security Monitoring](docs/SECURITY.md#-security-monitoring) - Audit logging and incident response

### 🔧 Technical Documentation
- [🏗️ Modular Architecture](docs/MODULAR_STRUCTURE.md) - Application structure and organization
- [🔄 Refactoring Summary](docs/REFACTORING_SUMMARY.md) - Recent code refactoring details
- [🐳 Docker Setup](docs/DOCKER_SETUP.md) - Docker configuration and deployment
- [🔧 Docker Compatibility](docs/DOCKER_COMPATIBILITY.md) - Docker-specific fixes and improvements
- [📧 Email Setup](docs/EMAIL_SETUP.md) - Email configuration for photo uploads
- [🔄 Immich Integration](docs/IMMICH_SETUP.md) - Immich server synchronization
- [🔐 SSO Setup](docs/sso_setup.md) - Single Sign-On authentication configuration

### 🛠️ Development & Debugging
- [🔧 PWA Debug Tools](docs/pwa.md#debugging) - PWA troubleshooting and testing
- [📱 Template Fixes](docs/TEMPLATE_FIXES.md) - Template routing and URL fixes
- [🐳 Docker Template Fix](docs/DOCKER_TEMPLATE_FIX.md) - Docker-specific template issues
- [📚 Documentation Organization](docs/ORGANIZATION_SUMMARY.md) - Documentation structure overview

### 📸 Visual Documentation
- [📸 Screenshots](#-screenshots) - Visual tour of the application

## 🔄 Recent Updates

### 🔒 Enhanced Security & Privacy (Latest)
Comprehensive security improvements to protect user privacy and data integrity:

- ✅ **File Upload Security**: Advanced file validation with magic byte detection and MIME type verification
- ✅ **Rate Limiting**: Multi-level rate limiting (application + nginx) to prevent abuse
- ✅ **Security Headers**: Comprehensive security headers including CSP, XSS protection, and HSTS
- ✅ **Audit Logging**: Detailed security event logging with configurable retention
- ✅ **Database Security**: WAL mode, secure pragmas, and file integrity checks
- ✅ **Input Validation**: Comprehensive input sanitization and validation
- ✅ **File Permissions**: Secure file permissions and access controls
- ✅ **Privacy Protection**: Data minimization and proper retention policies

### 🚀 Database Optimization & Performance (Latest)
Fixed database optimization issues and enhanced performance for large photo collections:

- ✅ **Database Optimizer Fix**: Fixed missing `is_enabled()` and `get_cache_size()` methods in DatabaseOptimizer class
- ✅ **Comprehensive Indexes**: Added 20+ database indexes for optimal query performance
- ✅ **Query Caching**: Implemented intelligent caching system with TTL for expensive queries
- ✅ **Connection Pooling**: Optimized SQLAlchemy connection pooling for better concurrency
- ✅ **Admin Dashboard**: Enhanced admin database monitoring with performance metrics
- ✅ **Migration Script**: Updated migration script to include all optimization indexes

### Lazy Loading Gallery
Added smooth infinite scroll for large photo galleries to improve performance and user experience:

- ✅ **Infinite Scroll**: Smooth scrolling that loads photos as you browse
- ✅ **Performance Optimization**: Faster initial load times and reduced server load
- ✅ **Loading Indicators**: Beautiful animated spinners while photos load
- ✅ **Filter Integration**: All search and filter features work seamlessly
- ✅ **Mobile Optimized**: Perfect performance on all devices

### Major Refactoring
The application has been completely refactored from a monolithic structure to a modern, modular Flask application:

- ✅ **Modular Architecture**: Converted from single `app.py` (3,000+ lines) to organized Blueprint structure
- ✅ **Enhanced Features**: Added comprehensive push notification system with web interface + browser notifications
- ✅ **Improved Performance**: Better code organization and maintainability
- ✅ **Docker Optimization**: Enhanced Docker compatibility and deployment
- ✅ **PWA Support**: Full Progressive Web App functionality with Service Worker
- ✅ **Debug Tools**: Comprehensive debugging panel for PWA and notification testing

**Key Improvements**:
- **50 files changed** with **5,359+ lines** of improved code
- **Flask Blueprints** for organized routing (`app/views/`, `app/models/`, `app/utils/`)
- **Application Factory Pattern** for better configuration management
- **Push Notification System** with dual web interface + browser notifications
- **Service Worker** for offline functionality and PWA support
- **Comprehensive Documentation** with detailed setup guides

## 🔒 Security Features

### 🛡️ Comprehensive Protection
- **File Upload Security**: Advanced validation with magic byte detection, MIME type verification, and dangerous file blocking
- **Rate Limiting**: Multi-level protection against abuse (5 uploads/5min, 10 API calls/min, 3 login attempts/min)
- **Security Headers**: Full suite of security headers including Content Security Policy, XSS protection, and HSTS
- **Audit Logging**: Detailed security event logging with 30-day retention and automatic cleanup
- **Database Security**: WAL mode, secure pragmas, file integrity checks, and restricted permissions
- **Input Validation**: Comprehensive sanitization and validation of all user inputs

### 🔐 Privacy Protection
- **Data Minimization**: Only necessary data is collected and logged
- **Anonymous Identifiers**: Rate limiting uses anonymous client identifiers
- **Secure Permissions**: Database and configuration files have restricted access
- **Audit Trail**: Complete audit trail for security monitoring and compliance

### 🚨 Security Monitoring
- **Real-time Logging**: All security events are logged with severity levels
- **Rate Limit Monitoring**: Track and respond to abuse attempts
- **File Integrity**: SHA-256 hash verification for uploaded files
- **Suspicious Activity Detection**: Automatic detection of malicious file uploads

## ✨ Quick Overview

### For Guests
- 📸 **Easy Photo/Video Upload** - No login required, drag-and-drop interface
- 🔍 **Search & Tagging** - Find photos quickly with search and custom tags
- ⚡ **Lazy Loading Gallery** - Smooth infinite scroll for large photo collections
- 📧 **Email Photo Upload** - Send photos directly via email
- 🤳 **Virtual Photobooth** - Take photos with custom wedding borders
- ❤️ **Like & Comment** - Interact with photos and videos
- 🔔 **Smart Notifications** - Get notified when someone interacts with your content
- 💌 **Message Board** - Share messages with optional photos
- 📖 **Virtual Guestbook** - Sign digital guestbook with photos
- 📱 **PWA Support** - Install as native app on mobile devices
- 🏆 **Photo of the Day** - Vote for daily featured photos with automatic candidate selection based on popularity
- 🎬 **Live Event Slideshow** - Real-time slideshow of all wedding activities with automatic updates

### For Admins
- 🔐 **Admin Dashboard** - Comprehensive management tools
- 🔐 **SSO Authentication** - Secure admin access with OAuth providers (Google, Azure, Okta)
- 📊 **Statistics** - View usage analytics and content metrics
- 📧 **Email Configuration** - Set up automatic photo processing
- 🔄 **Immich Sync** - Sync to your own Immich server
- 📱 **PWA Debug Tools** - Monitor and troubleshoot PWA issues
- 💾 **Batch Download** - Download all content as ZIP file
- 🏆 **Photo of the Day Management** - Select and manage daily featured photos with automatic candidate system
- ⚡ **Database Optimization** - Optimized for thousands of photos with caching and maintenance tools
- 🔒 **Security Monitoring** - Comprehensive security audit logs and monitoring tools

## 📸 Screenshots

### Gallery & Upload
![Gallery View](docs/screenshots/gallery-view.png)
*Main gallery showing uploaded photos and videos with like/comment functionality*

![Upload Interface](docs/screenshots/upload-interface.png)
*Easy photo and video upload with drag-and-drop support*

### Mobile Experience
![Mobile Gallery](docs/screenshots/mobile-gallery.png)
*Responsive design optimized for mobile devices*

![PWA Installation](docs/screenshots/pwa-install.png)
*Progressive Web App installation prompt on mobile*

### Admin Dashboard
![Admin Dashboard](docs/screenshots/admin-dashboard.png)
*Comprehensive admin panel with statistics and management tools*

![PWA Debug Tools](docs/screenshots/pwa-debug.png)
*PWA debugging and troubleshooting tools*

### Interactive Features
![Virtual Photobooth](docs/screenshots/photobooth.png)
*Virtual photobooth with custom wedding borders*

![Message Board](docs/screenshots/message-board.png)
*Interactive message board with photo sharing*

![Guestbook](docs/screenshots/guestbook.png)
*Digital guestbook with photo attachments*

![Photo of the Day](docs/screenshots/photo-of-day.png)
*Daily photo voting system with engagement tracking*

## 🚀 Quick Start

### Using Docker (Recommended)
```bash
git clone https://github.com/chartmann1590/VowVault.git
cd VowVault
docker-compose up -d
```

### Manual Installation
```bash
git clone https://github.com/chartmann1590/VowVault.git
cd VowVault
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
pip install -r requirements.txt
python migration.py
python run.py
```

**Access:** 
- Gallery: http://localhost
- Admin: http://localhost/admin?key=wedding2024
- SSO Login: http://localhost/sso/login (when SSO is enabled)

## 📚 Documentation

For detailed information, see our comprehensive documentation:

- **[Features](docs/features.md)** - Complete feature breakdown and capabilities
- **[Installation Guide](docs/installation.md)** - Setup instructions and troubleshooting
- **[SSO Setup](docs/sso_setup.md)** - Configure secure admin authentication
- **[Usage Guide](docs/usage.md)** - Step-by-step user instructions
- **[PWA Guide](docs/pwa.md)** - Progressive Web App setup and troubleshooting
- **[Photo of the Day](docs/photo_of_day.md)** - Daily photo voting system documentation

## 🔧 Configuration

### Security
- Change the default admin key in `app.py`
- Enable SSO authentication for enhanced security
- Set up HTTPS/SSL for production
- Configure proper backup strategy

### Environment Variables
Copy `env.example` to `.env` and configure:
- Email settings for photo uploads
- Immich server sync settings
- Database configuration

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Submit a pull request

## 📄 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## 🙏 Acknowledgments

- Built with [Flask](https://flask.palletsprojects.com/)
- Icons by [Feather Icons](https://feathericons.com/)
- PWA implementation with modern web standards
- Beautiful design inspired by wedding aesthetics

---

**Made with ❤️ for your special day**

*Created by [Charles Hartmann](https://github.com/chartmann1590)*