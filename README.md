# 💑 Wedding Photo Gallery

A beautiful, self-hosted wedding photo gallery application that allows wedding guests to upload and share photos without requiring any login. Built with Flask and designed with love for your special day.

![Python](https://img.shields.io/badge/python-3.11-blue.svg)
![Flask](https://img.shields.io/badge/flask-3.0-green.svg)
![Docker](https://img.shields.io/badge/docker-ready-blue.svg)
![License](https://img.shields.io/badge/license-MIT-green.svg)

## ✨ Features

### For Guests
- 📸 **Easy Photo/Video Upload** - No login required, just upload and share
- ❤️ **Like Photos/Videos** - Show appreciation for beautiful moments
- 💬 **Leave Comments** - Share memories and messages on photos
- 💌 **Message Board** - Post messages with optional photos that everyone can see, like, and comment on
- 📖 **Virtual Guestbook** - Sign a digital guestbook with wishes and optional photos
- 📱 **Mobile Responsive** - Works perfectly on all devices
- 🎉 **Welcome Modal** - Greet guests with a personalized message

### For Admins
- 🔐 **Admin Dashboard** - Secure admin area with simple key authentication
- 📊 **Statistics** - View total photos, likes, comments, messages, and guestbook entries
- 🗑️ **Content Management** - Delete inappropriate photos, messages, or guestbook entries
- 👁️ **Hide/Show Messages** - Hide inappropriate messages without deleting them
- ✏️ **Edit Guestbook** - Modify guestbook entries when needed
- 🖼️ **Media Management** - View and manage photos attached to messages and guestbook entries
- 📄 **QR Code Generator** - Create beautiful PDFs with QR codes for easy sharing
- ✏️ **Customizable Content** - Edit welcome messages and QR code content

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
- Maximum file size: 16MB (configurable)
- Allowed formats: PNG, JPG, JPEG, GIF, WEBP

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
│   ├── photo_detail.html # Photo detail page
│   ├── message_board.html # Message board
│   ├── new_message.html  # Post new message
│   ├── admin.html       # Admin dashboard
│   ├── guestbook.html   # View guestbook
│   └── sign_guestbook.html # Sign guestbook
├── static/              # Static files
│   └── uploads/        # Uploaded photos (created automatically)
│       ├── guestbook/  # Guestbook photos
│       └── messages/   # Message board photos
└── data/               # Database files (created automatically)
```

## 🎨 Customization

### Welcome Modal
1. Go to Admin Dashboard
2. Find "Welcome Modal Settings"
3. Customize:
   - Title and message
   - Upload a couple photo URL
   - Edit instructions for guests
   - Choose to show once or always

### QR Code PDFs
1. Set your public gallery URL
2. Customize the PDF content
3. Generate and print for your venue

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
# Backup photos and database
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

2. **Upload Photos**
   - Click "Upload Photo"
   - Select your photo
   - Add your name (optional)
   - Add a description (optional)
   - Click "Upload"

3. **Interact with Photos**
   - Click any photo to view details
   - Click the heart to like
   - Leave comments with your name

4. **Post on Message Board**
   - Click "Message Board" in navigation
   - Click "Leave a Message"
   - Enter your name (optional)
   - Write your message
   - Add a photo (optional)
   - Submit your message
   - Like and comment on other messages

5. **Sign the Guestbook**
   - Click "Guestbook" in navigation
   - Click "Sign the Guestbook"
   - Enter your name and location (optional)
   - Write your message
   - Add a photo (optional)
   - Submit your entry

### For Administrators

1. **Access Admin Panel**
   - Visit `/admin?key=your-key`
   - View statistics including message board activity
   - Manage photos, messages, and guestbook entries

2. **Manage Message Board**
   - View all messages with their comments
   - Hide inappropriate messages (they remain in database but hidden from public)
   - Unhide previously hidden messages
   - Delete messages permanently
   - View and manage message comments

3. **Manage Guestbook**
   - View all guestbook entries
   - Edit entries to fix typos
   - Delete inappropriate entries
   - View photos attached to entries

4. **Generate QR Codes**
   - Enter your public URL
   - Customize the message
   - Download PDF
   - Print for tables

## 🐛 Troubleshooting

### Common Issues

**Photos not uploading:**
- Check file size (max 16MB)
- Ensure correct file format
- Check disk space

**Message board not loading:**
- Ensure database migrations have run
- Check that the `/static/uploads/messages` directory exists
- Verify write permissions

**Admin panel not accessible:**
- Verify the admin key
- Check URL format: `/admin?key=your-key`

**Docker issues:**
- Ensure ports 80/5000 are available
- Check Docker logs: `docker-compose logs`

**Database migration errors:**
- Ensure the migration script has run
- Check database file permissions
- Verify all directories exist

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

---

Made with ❤️ for your special day