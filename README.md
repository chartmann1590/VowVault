# 💑 Wedding Photo Gallery

A beautiful, self-hosted wedding photo gallery application that allows wedding guests to upload and share photos without requiring any login. Built with Flask and designed with love for your special day.

![Python](https://img.shields.io/badge/python-3.11-blue.svg)
![Flask](https://img.shields.io/badge/flask-3.0-green.svg)
![Docker](https://img.shields.io/badge/docker-ready-blue.svg)
![License](https://img.shields.io/badge/license-MIT-green.svg)

## ✨ Features

### For Guests
- 📸 **Easy Photo Upload** - No login required, just upload and share
- ❤️ **Like Photos** - Show appreciation for beautiful moments
- 💬 **Leave Comments** - Share memories and messages
- 📱 **Mobile Responsive** - Works perfectly on all devices
- 🎉 **Welcome Modal** - Greet guests with a personalized message

### For Admins
- 🔐 **Admin Dashboard** - Secure admin area with simple key authentication
- 📊 **Statistics** - View total photos, likes, and comments
- 🗑️ **Photo Management** - Delete inappropriate photos
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

2. Create templates directory and copy all template files

3. Run the application:
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
├── Dockerfile             # Docker container definition
├── docker-compose.yml     # Docker Compose configuration
├── nginx.conf            # Nginx configuration for production
├── templates/            # HTML templates
│   ├── base.html        # Base template
│   ├── index.html       # Gallery page
│   ├── upload.html      # Upload page
│   ├── photo_detail.html # Photo detail page
│   └── admin.html       # Admin dashboard
├── static/              # Static files
│   └── uploads/        # Uploaded photos (created automatically)
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

### For Administrators

1. **Access Admin Panel**
   - Visit `/admin?key=your-key`
   - View statistics
   - Manage photos

2. **Generate QR Codes**
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

**Admin panel not accessible:**
- Verify the admin key
- Check URL format: `/admin?key=your-key`

**Docker issues:**
- Ensure ports 80/5000 are available
- Check Docker logs: `docker-compose logs`

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