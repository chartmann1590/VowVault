# Wedding Gallery Documentation

Welcome to the Wedding Gallery documentation. This directory contains comprehensive documentation for the application, including setup guides, feature descriptions, and technical details.

## 📚 Documentation Index

### 🚀 Getting Started
- **[Installation Guide](installation.md)** - How to install and set up the Wedding Gallery
- **[Usage Guide](usage.md)** - How to use the Wedding Gallery features
- **[Features Overview](features.md)** - Complete list of features and capabilities

### 🔧 Technical Documentation
- **[Modular Structure](MODULAR_STRUCTURE.md)** - Architecture and organization of the codebase
- **[Refactoring Summary](REFACTORING_SUMMARY.md)** - Summary of the modular refactoring
- **[Docker Setup](DOCKER_SETUP.md)** - Complete Docker deployment guide
- **[Docker Compatibility](DOCKER_COMPATIBILITY.md)** - Docker compatibility changes and testing

### 🔐 Authentication & Security
- **[SSO Setup](sso_setup.md)** - Single Sign-On configuration guide

### 📱 Progressive Web App
- **[PWA Features](pwa.md)** - Progressive Web App functionality and setup

### 🔗 Integrations
- **[Email Setup](EMAIL_SETUP.md)** - Email integration configuration
- **[Immich Setup](IMMICH_SETUP.md)** - Immich photo server integration

### 🛠️ Admin Dashboard
- **[Admin Dashboard Guide](ADMIN_DASHBOARD.md)** - Complete admin dashboard documentation
- **[Admin Organization](ADMIN_ORGANIZATION.md)** - Admin page organization and navigation
- **[QR Code Feature](qr_code.md)** - QR code generation and configuration

### 📸 Screenshots
- **[Screenshots](screenshots/)** - Visual examples of the application

## 🏗️ Architecture Overview

The Wedding Gallery is built using a modular Flask architecture with the following structure:

```
Wedding/
├── app/                          # Main application package
│   ├── __init__.py              # Application factory
│   ├── models/                  # Database models
│   ├── views/                   # Route handlers (Blueprints)
│   └── utils/                   # Utility functions
├── docs/                        # Documentation
├── templates/                   # HTML templates
├── static/                      # Static files
└── run.py                       # Application entry point
```

## 🚀 Quick Start

### Local Development
```bash
# Clone the repository
git clone <repository-url>
cd Wedding

# Set up virtual environment
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt

# Run the application
python run.py
```

### Docker Deployment
```bash
# Build and run with Docker Compose
docker-compose up --build

# Or build and run with Docker
docker build -t wedding-gallery .
docker run -p 5000:5000 wedding-gallery
```

## 📋 Key Features

- **Photo & Video Upload** - Upload and share wedding photos and videos
- **Guestbook** - Digital guestbook with photo attachments
- **Message Board** - Community message board for guests
- **Virtual Photobooth** - Interactive photobooth with custom borders
- **Email Integration** - Upload photos via email
- **Immich Sync** - Sync photos to Immich photo server
- **SSO Authentication** - Single Sign-On for admin access
- **PWA Support** - Progressive Web App functionality
- **Comprehensive Admin Dashboard** - Complete admin interface with navigation
- **QR Code Generation** - Generate QR codes for easy sharing
- **System Logs** - Monitor email processing and sync activities
- **Database Maintenance** - Database optimization and maintenance tools
- **Slideshow Settings** - Configure photo slideshow functionality

## 🔧 Configuration

The application can be configured through:
- Environment variables
- Database settings
- Email configuration
- SSO provider settings
- Immich integration settings

See the individual documentation files for detailed configuration instructions.

## 🆕 Recent Updates

### Admin Dashboard Improvements (Latest)
- **Enhanced Navigation**: Added comprehensive navigation system to main admin dashboard
- **New Admin Pages**: Added System Logs and Database Maintenance pages
- **Improved Organization**: Organized admin pages into logical categories
- **Better User Experience**: Added visual icons, hover effects, and responsive design
- **Complete Coverage**: All admin functionality now accessible through navigation

### Admin Page Categories
- **Content Management**: Photos & Videos, Guestbook, Message Board, Slideshow Settings
- **Settings & Configuration**: Photobooth, QR Codes, Welcome Modal, SSO, CAPTCHA
- **Integrations & Services**: Email Settings, Immich Sync, Push Notifications
- **System & Maintenance**: System Logs, Database Maintenance

## 🐛 Troubleshooting

### Common Issues
1. **Database Issues** - Check the [Installation Guide](installation.md)
2. **Docker Problems** - See [Docker Setup](DOCKER_SETUP.md)
3. **Email Configuration** - Review [Email Setup](EMAIL_SETUP.md)
4. **SSO Issues** - Check [SSO Setup](sso_setup.md)
5. **Immich Integration** - See [Immich Setup](IMMICH_SETUP.md)

### Getting Help
- Check the relevant documentation file
- Review the troubleshooting sections
- Test with the provided test scripts

## 📝 Contributing

When contributing to the Wedding Gallery:

1. Follow the modular structure
2. Add documentation for new features
3. Update this index when adding new docs
4. Test thoroughly before submitting

## 📄 License

This project is licensed under the MIT License - see the LICENSE file for details.

---

For questions or issues, please refer to the specific documentation files or create an issue in the repository. 