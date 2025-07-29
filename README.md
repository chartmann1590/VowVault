# 💑 VowVault - Wedding Photo Gallery

A beautiful, self-hosted wedding photo gallery application that allows wedding guests to upload and share photos without requiring any login. Built with Flask and designed with love for your special day.

![Python](https://img.shields.io/badge/python-3.11-blue.svg)
![Flask](https://img.shields.io/badge/flask-3.0-green.svg)
![Docker](https://img.shields.io/badge/docker-ready-blue.svg)
![License](https://img.shields.io/badge/license-MIT-green.svg)

## 📋 Table of Contents

- [✨ Features](docs/features.md) - Complete feature overview for guests and admins
- [🚀 Installation Guide](docs/installation.md) - Quick start and production deployment
- [📱 Usage Guide](docs/usage.md) - Step-by-step instructions for guests and admins
- [📱 Progressive Web App](docs/pwa.md) - PWA installation and troubleshooting
- [📸 Screenshots](#-screenshots) - Visual tour of the application

## ✨ Quick Overview

### For Guests
- 📸 **Easy Photo/Video Upload** - No login required, drag-and-drop interface
- 📧 **Email Photo Upload** - Send photos directly via email
- 🤳 **Virtual Photobooth** - Take photos with custom wedding borders
- ❤️ **Like & Comment** - Interact with photos and videos
- 💌 **Message Board** - Share messages with optional photos
- 📖 **Virtual Guestbook** - Sign digital guestbook with photos
- 📱 **PWA Support** - Install as native app on mobile devices

### For Admins
- 🔐 **Admin Dashboard** - Comprehensive management tools
- 📊 **Statistics** - View usage analytics and content metrics
- 📧 **Email Configuration** - Set up automatic photo processing
- 🔄 **Immich Sync** - Sync to your own Immich server
- 📱 **PWA Debug Tools** - Monitor and troubleshoot PWA issues
- 💾 **Batch Download** - Download all content as ZIP file

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
python app.py
```

**Access:** 
- Gallery: http://localhost
- Admin: http://localhost/admin?key=wedding2024

## 📚 Documentation

For detailed information, see our comprehensive documentation:

- **[Features](docs/features.md)** - Complete feature breakdown and capabilities
- **[Installation Guide](docs/installation.md)** - Setup instructions and troubleshooting
- **[Usage Guide](docs/usage.md)** - Step-by-step user instructions
- **[PWA Guide](docs/pwa.md)** - Progressive Web App setup and troubleshooting

## 🔧 Configuration

### Security
- Change the default admin key in `app.py`
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