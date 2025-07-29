# 🚀 Installation Guide

## Quick Start

### Using Docker (Recommended)

1. **Clone the repository:**
```bash
git clone https://github.com/chartmann1590/VowVault.git
cd VowVault
```

2. **Create necessary directories:**
```bash
mkdir -p uploads data
```

3. **Build and run with Docker Compose:**
```bash
docker-compose up -d
```

The migration script will run automatically when the container starts.

4. **Access the application:**
- Gallery: http://localhost
- Admin: http://localhost/admin?key=wedding2024

### Manual Installation

1. **Clone and setup:**
```bash
git clone https://github.com/chartmann1590/VowVault.git
cd VowVault
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
pip install -r requirements.txt
```

2. **Run the migration script:**
```bash
python migration.py
```

3. **Create templates directory and copy all template files**

4. **Run the application:**
```bash
python app.py
```

## Production Deployment

### Using Docker

1. **Update `nginx.conf` with your domain**
2. **Set up SSL certificates**
3. **Update environment variables**
4. **Deploy:**
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

## Configuration

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
- Video formats: MP4, MOV, AVI (max 15 seconds)

### Environment Variables
Copy `env.example` to `.env` and configure your settings:
```bash
cp env.example .env
# Edit .env with your actual values
```

### Git Configuration
The `.gitignore` file is configured to exclude:
- Virtual environment (`venv/`)
- Database files (`*.db`, `*.sqlite`)
- Upload directories (`static/uploads/`)
- Environment files (`.env`)
- Email credentials and logs
- Python cache files (`__pycache__/`)

## Backup Strategy

### Using the Built-in Feature (Recommended)
Access: `/admin/batch-download?key=your-key`

### Manual Backup
```bash
# Create backup
tar -czf backup-$(date +%Y%m%d).tar.gz uploads/ data/

# Restore
tar -xzf backup-20240101.tar.gz
```

## Troubleshooting

### Common Issues

1. **Port already in use:**
   - Change port in `app.py` or Docker configuration
   - Kill existing processes using the port

2. **Permission errors:**
   - Ensure proper file permissions on upload directories
   - Check Docker volume permissions

3. **Database migration errors:**
   - Run `python migration.py` manually
   - Check database file permissions

4. **Email not working:**
   - Verify SMTP settings in admin panel
   - Check firewall settings
   - Test with different email providers

### PWA Issues

1. **HTTPS Required:**
   - PWA features only work with valid SSL certificates
   - Self-signed certificates won't work
   - Use Let's Encrypt or similar for production

2. **Installation Problems:**
   - Check browser console for errors
   - Use PWA debug tools in admin panel
   - Verify manifest.json is accessible

### Notification Issues

1. **Notifications Not Working:**
   - Check browser notification permissions
   - Verify HTTPS setup (required for notifications)
   - Test on supported browsers (Chrome, Firefox, Safari)
   - Check mobile hamburger menu toggle status

2. **Permission Denied:**
   - Guide users to browser settings
   - Explain notification benefits
   - Provide manual permission instructions

3. **Self-Notifications:**
   - System is designed to exclude self-notifications
   - Only others' interactions trigger notifications
   - This is intentional behavior

### Performance Optimization

1. **Large galleries:**
   - Consider using PostgreSQL for better performance
   - Implement pagination for large photo collections
   - Optimize image sizes before upload

2. **High traffic:**
   - Use a reverse proxy (nginx)
   - Implement caching
   - Consider CDN for static assets 