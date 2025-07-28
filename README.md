# 💑 Wedding Photo Gallery

A beautiful, self-hosted wedding photo gallery application that allows wedding guests to upload and share photos without requiring any login. Built with Flask and designed with love for your special day.

![Python](https://img.shields.io/badge/python-3.11-blue.svg)
![Flask](https://img.shields.io/badge/flask-3.0-green.svg)
![Docker](https://img.shields.io/badge/docker-ready-blue.svg)
![License](https://img.shields.io/badge/license-MIT-green.svg)

## ✨ Features

### For Guests
- 📸 **Easy Photo/Video Upload** - No login required, just upload and share (photos and videos up to 50MB, videos max 15 seconds)
- 🤳 **Virtual Photobooth** - Take photos with custom wedding borders using device camera
- ❤️ **Like Photos/Videos** - Show appreciation for beautiful moments
- 💬 **Leave Comments** - Share memories and messages on photos and videos
- 💌 **Message Board** - Post messages with optional photos that everyone can see, like, and comment on
- 📖 **Virtual Guestbook** - Sign a digital guestbook with wishes and optional photos
- 📱 **Mobile Responsive** - Works perfectly on all devices
- 🎉 **Welcome Modal** - Greet guests with a personalized message and instructions

### For Admins
- 🔐 **Admin Dashboard** - Secure admin area with simple key authentication
- 📊 **Statistics** - View total photos, videos, likes, comments, messages, guestbook entries, and photobooth photos
- 🗑️ **Content Management** - Delete inappropriate photos, messages, or guestbook entries
- 👁️ **Hide/Show Messages** - Hide inappropriate messages without deleting them
- ✏️ **Edit Guestbook** - Modify guestbook entries when needed
- 🖼️ **Media Management** - View and manage photos attached to messages and guestbook entries
- 🎨 **Photobooth Border Upload** - Upload custom borders for the virtual photobooth
- 📄 **QR Code Generator** - Create beautiful PDFs with QR codes for easy sharing
- ✏️ **Customizable Content** - Edit welcome messages, modal settings, and QR code content
- 💾 **Batch Download** - Download all gallery content (photos, videos, data) as a comprehensive ZIP file
- 🔄 **System Reset** - Complete system reset with confirmation to start fresh

## 🚀 Quick Start

### Using Docker (Recommended)

1. Clone the repository:
```bash
git clone https://github.com/chartmann1590/WeddingShare.git
cd WeddingShare
```

2. Create necessary directories:
```bash
mkdir -p uploads data
```

3. Build and run with Docker Compose:
```bash
docker-compose up -d
```

The migration script will run automatically when the container starts.

4. Access the application:
- Gallery: http://localhost
- Admin: http://localhost/admin?key=wedding2024

### Manual Installation

1. Clone and setup:
```bash
git clone https://github.com/chartmann1590/WeddingShare.git
cd WeddingShare
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
pip install -r requirements.txt
```

2. Run the migration script:
```bash
python migration.py
```

3. Create templates directory and copy all template files

4. Run the application:
```bash
python app.py
```

## 🔧 Configuration

### Admin Access
Change the admin key in `app.py`:
```python
if admin_key != 'wedding2024':  # Change this!
```

### Database
By default, uses SQLite. For production with many users, consider PostgreSQL:
```python
app.config['SQLALCHEMY_DATABASE_URI'] = 'postgresql://user:pass@localhost/dbname'
```

### File Uploads
- Maximum file size: 50MB (supports both photos and videos)
- Photo formats: PNG, JPG, JPEG, GIF, WEBP
- Video formats: MP4, MOV, AVI, WEBM (max 15 seconds)

## 📁 Project Structure

```
wedding-photo-gallery/
├── app.py                  # Main Flask application
├── requirements.txt        # Python dependencies
├── migration.py           # Database migration script
├── Dockerfile             # Docker container definition
├── docker-compose.yml     # Docker Compose configuration
├── nginx.conf            # Nginx configuration for production
├── templates/            # HTML templates
│   ├── base.html        # Base template
│   ├── index.html       # Gallery page
│   ├── upload.html      # Upload page
│   ├── photo_detail.html # Photo/video detail page
│   ├── photobooth.html  # Virtual photobooth
│   ├── message_board.html # Message board
│   ├── new_message.html  # Post new message
│   ├── admin.html       # Admin dashboard
│   ├── guestbook.html   # View guestbook
│   ├── sign_guestbook.html # Sign guestbook
│   ├── privacy_policy.html # Privacy policy page
│   └── terms_of_use.html   # Terms of use page
├── static/              # Static files
│   └── uploads/        # Uploaded content (created automatically)
│       ├── guestbook/  # Guestbook photos
│       ├── messages/   # Message board photos
│       ├── videos/     # Video uploads
│       ├── thumbnails/ # Video thumbnails
│       ├── photobooth/ # Photobooth photos
│       └── borders/    # Photobooth border images
└── data/               # Database files (created automatically)
```

## 🎨 Customization

### Virtual Photobooth
1. Go to Admin Dashboard
2. Find "Virtual Photobooth Settings"
3. Upload a custom border image:
   - Use PNG format with transparent areas where the photo will show
   - Recommended size: 1280x720px or 16:9 aspect ratio
   - The border will overlay on top of the camera feed
4. Guests can then access the photobooth and take photos with your custom border

### Welcome Modal
1. Go to Admin Dashboard
2. Find "Welcome Modal Settings"
3. Customize:
   - Enable/disable the modal
   - Title and message
   - Upload a couple photo URL
   - Edit instructions for guests
   - Choose to show once or always

### QR Code PDFs
1. Set your public gallery URL
2. Customize the PDF content (title, subtitle, message, couple names)
3. Generate and print for your venue

### Video Support
- Automatic video thumbnail generation using FFmpeg
- Video duration validation (max 15 seconds)
- Support for multiple video formats
- Mobile-friendly video playback

### Styling
The app uses a warm, elegant color scheme perfect for weddings. To customize:
- Colors are defined in CSS within each template
- Main colors: `#8b7355` (primary), `#6b5d54` (secondary)

## 🚢 Production Deployment

### Using Docker

1. Update `nginx.conf` with your domain
2. Set up SSL certificates
3. Update environment variables
4. Deploy:
```bash
docker-compose -f docker-compose.prod.yml up -d
```

### Security Checklist
- [ ] Change admin key from default
- [ ] Set up HTTPS/SSL
- [ ] Configure proper backup strategy
- [ ] Set up monitoring
- [ ] Implement rate limiting
- [ ] Configure firewall rules

### Backup Strategy
```bash
# Using the built-in batch download feature (recommended)
# Access: /admin/batch-download?key=your-key

# Or manual backup
tar -czf backup-$(date +%Y%m%d).tar.gz uploads/ data/

# Restore
tar -xzf backup-20240101.tar.gz
```

## 📱 Usage Guide

### For Wedding Guests

1. **Visit the Gallery**
   - Scan the QR code or visit the URL
   - View the welcome message
   - Choose to sign the guestbook, post a message, or enter the gallery

2. **Upload Photos/Videos**
   - Click "Upload Photo/Video"
   - Select your photo or video (videos max 15 seconds, files max 50MB)
   - Add your name (optional)
   - Add a description (optional)
   - Click "Upload"

3. **Use Virtual Photobooth**
   - Click "Virtual Photobooth" in navigation or from the welcome screen
   - Allow camera access when prompted
   - Position yourself in the frame with the wedding border overlay
   - Click "Take Photo" (3-second countdown)
   - Download the photo or upload it directly to the gallery

4. **Interact with Photos/Videos**
   - Click any photo or video to view details
   - Click the heart to like
   - Leave comments with your name
   - Videos play with controls and show duration

5. **Post on Message Board**
   - Click "Message Board" in navigation
   - Click "Leave a Message"
   - Enter your name (optional)
   - Write your message
   - Add a photo (optional)
   - Submit your message
   - Like and comment on other messages

6. **Sign the Guestbook**
   - Click "Guestbook" in navigation
   - Click "Sign the Guestbook"
   - Enter your name and location (optional)
   - Write your message
   - Add a photo (optional)
   - Submit your entry

### For Administrators

1. **Access Admin Panel**
   - Visit `/admin?key=your-key`
   - View comprehensive statistics including photobooth usage
   - Manage photos, videos, messages, and guestbook entries

2. **Batch Download All Content**
   - Click "Download All Content" button
   - Automatically downloads a ZIP file containing:
     - All photos organized by type (photos/, videos/, photobooth/, etc.)
     - All video thumbnails
     - All guestbook and message photos
     - Complete database export as JSON
     - Photobooth border images

3. **System Reset**
   - Click "System Reset" button for complete data wipe
   - Must type "RESET EVERYTHING" to confirm
   - Deletes all database records and uploaded files
   - Returns system to fresh state

4. **Configure Virtual Photobooth**
   - Upload a custom border image (PNG with transparency recommended)
   - The border will appear as an overlay on the camera feed
   - Test the photobooth to ensure the border looks good
   - Monitor photobooth photo statistics

5. **Manage Message Board**
   - View all messages with their comments (visible/hidden tabs)
   - Hide inappropriate messages (they remain in database but hidden from public)
   - Unhide previously hidden messages
   - Delete messages permanently
   - View and manage message comments

6. **Manage Guestbook**
   - View all guestbook entries
   - Edit entries to fix typos or inappropriate content
   - Delete inappropriate entries
   - View photos attached to entries

7. **Configure Welcome Modal**
   - Enable/disable the welcome modal
   - Set custom title, message, and instructions
   - Add couple photo URL
   - Choose whether to show once per user or always

8. **Generate QR Codes**
   - Enter your public URL
   - Customize the message and couple names
   - Download professionally designed PDF
   - Print for tables or wedding programs

## 🐛 Troubleshooting

### Common Issues

**Photos/Videos not uploading:**
- Check file size (max 50MB)
- Ensure correct file format
- Check disk space
- For videos: ensure duration is under 15 seconds

**Virtual Photobooth not working:**
- Ensure HTTPS is enabled (camera access requires secure connection)
- Check browser camera permissions
- Verify border image is uploaded correctly
- Try refreshing the page

**Videos not playing:**
- Ensure ffmpeg is installed (included in Docker image)
- Check video format compatibility
- Verify video is under 15 seconds

**Message board not loading:**
- Ensure database migrations have run
- Check that the `/static/uploads/messages` directory exists
- Verify write permissions

**Admin panel not accessible:**
- Verify the admin key
- Check URL format: `/admin?key=your-key`

**Batch download fails:**
- Check disk space for temporary ZIP file creation
- Ensure all upload directories are accessible
- Verify admin permissions

**System reset not working:**
- Ensure exact confirmation text: "RESET EVERYTHING"
- Check file system permissions for deletion
- Verify database write access

**Docker issues:**
- Ensure ports 80/5000 are available
- Check Docker logs: `docker-compose logs`

**Database migration errors:**
- Ensure the migration script has run
- Check database file permissions
- Verify all directories exist

## 🆕 What's New

### Latest Features
- **Video Support**: Upload and share wedding videos (max 15 seconds, 50MB)
- **Automatic Thumbnails**: Video thumbnails generated automatically with FFmpeg
- **Batch Download**: Complete backup of all content in organized ZIP file
- **System Reset**: Admin can completely reset the system with confirmation
- **Enhanced Admin Dashboard**: Better organization and new management tools
- **Improved Mobile Experience**: Better responsive design for all devices
- **Privacy & Terms Pages**: Professional legal pages for transparency

### Recent Improvements
- Better error handling for large files
- Improved video playback controls
- Enhanced security for admin functions
- More comprehensive statistics tracking
- Better organization of uploaded content

## 🤝 Contributing

Contributions are welcome! Please:
1. Fork the repository
2. Create a feature branch
3. Commit your changes
4. Push to the branch
5. Open a Pull Request

## 📄 License

This project is licensed under the MIT License - see the LICENSE file for details.

## 🙏 Acknowledgments

- Built with love for couples everywhere
- Inspired by the joy of wedding celebrations
- Thanks to all contributors
- Special thanks to the Flask and Python communities

---

Made with ❤️ for your special day