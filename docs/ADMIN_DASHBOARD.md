# Admin Dashboard Guide

> **Update (2024):** All admin templates are now linked to the admin dashboard and their SQL database counterparts. The `/dashboard` route is now available as an alias for the main admin dashboard (`/admin`). All navigation and database integration is up to date.

The Wedding Gallery features a comprehensive admin dashboard that provides complete control over all aspects of the application. This guide covers the admin interface, navigation, and all available admin pages.

## 🚀 Accessing the Admin Dashboard

### URL Access
```
http://your-domain.com/admin?key=wedding2024
```

### SSO Authentication
If SSO is enabled, you can access the admin dashboard through SSO authentication:
```
http://your-domain.com/sso/login
```

## 📊 Main Admin Dashboard

The main admin dashboard (`/admin`) provides:

### Statistics Overview
- Total photos and videos
- Total likes and comments
- Guestbook entries count
- Message board posts
- Photobooth photos count

### Quick Actions
- **Download All Content** - Batch download all photos and data
- **System Reset** - Complete system reset (destructive action)
- **PWA Debug** - Debug Progressive Web App functionality
- **Notification Users** - Manage push notification users


### Comprehensive Navigation
The admin dashboard includes organized navigation to all admin pages:

## 📁 Admin Page Categories

### 🖼️ Content Management

#### Photos & Videos (`/admin/photos`)
- View all uploaded photos and videos
- Delete photos and videos
- Manage photo metadata
- View upload statistics

#### Guestbook (`/admin/guestbook`)
- View all guestbook entries
- Edit guestbook entries
- Delete entries
- Manage guestbook photos

#### Message Board (`/admin/messages`)
- View all message board posts
- Hide/show messages
- Delete messages
- Manage message comments
- View message statistics

#### Slideshow Settings (`/admin/slideshow`)
- Configure slideshow behavior
- Set slideshow timing
- Manage slideshow content
- Preview slideshow settings

### ⚙️ Settings & Configuration

#### Photobooth Settings (`/admin/photobooth`)
- Upload custom wedding borders
- Configure photobooth options
- Set border positioning
- Preview photobooth functionality

#### QR Code Settings (`/admin/qr-settings`)
- Generate QR codes for sharing
- Customize QR code content
- Set public gallery URL
- Download QR code PDFs

#### Welcome Modal (`/admin/welcome-modal`)
- Configure welcome message
- Set modal appearance
- Add couple photo
- Customize instructions

#### SSO Settings (`/admin/sso-settings`)
- Configure Single Sign-On
- Set up OAuth providers
- Manage allowed domains
- Configure authentication flow

#### CAPTCHA Settings (`/admin/captcha-settings`)
- Enable/disable CAPTCHA protection
- Configure protection areas
- Set CAPTCHA difficulty
- Manage spam prevention

#### Timezone Settings (`/admin/timezone-settings`)
- Configure admin timezone preferences
- View all dates/times in local timezone
- Select from comprehensive timezone list
- Real-time timezone preview
- Affects all admin interface date displays

### 🔗 Integrations & Services

#### Email Settings (`/admin/email-settings`)
- Configure email photo upload
- Set up SMTP settings
- Configure IMAP monitoring
- Manage email responses
- View email processing logs

#### Immich Sync (`/admin/immich-settings`)
- Configure Immich server connection
- Set sync options
- Manage album settings
- View sync logs
- Test sync functionality

#### Push Notifications (`/admin/notification-users`)
- View notification users
- Send push notifications
- Manage notification settings
- View notification statistics

### 🛠️ System & Maintenance

#### System Logs (`/admin/logs`)
- View email processing logs
- Monitor Immich sync logs
- Filter logs by status
- Export log data

#### Database Maintenance (`/admin/database`)
- View database statistics
- Optimize database performance
- Clear cache
- Perform maintenance tasks

## 🎨 Admin Interface Features

### Visual Design
- **Modern UI**: Clean, professional interface
- **Responsive Design**: Works on desktop and mobile
- **Color Scheme**: Wedding-themed colors (#8b7355, #6b5d54)
- **Typography**: Playfair Display for headings

### Navigation Features
- **Organized Categories**: Logical grouping of admin pages
- **Visual Icons**: SVG icons for each admin section
- **Hover Effects**: Interactive navigation elements
- **Back Links**: Easy navigation back to main dashboard

### Status Indicators
- **Active/Inactive Status**: Visual indicators for features
- **Real-time Updates**: Live status of integrations
- **Error Handling**: Clear error messages and states

## 🔧 Admin Functions

### Content Management
```bash
# Access photo management
/admin/photos?key=wedding2024

# Access guestbook management
/admin/guestbook?key=wedding2024

# Access message board management
/admin/messages?key=wedding2024
```

### Settings Configuration
```bash
# Access photobooth settings
/admin/photobooth?key=wedding2024

# Access QR code settings
/admin/qr-settings?key=wedding2024

# Access welcome modal settings
/admin/welcome-modal?key=wedding2024
```

### System Administration
```bash
# Access system logs
/admin/logs?key=wedding2024

# Access database maintenance
/admin/database?key=wedding2024
```

## 🔐 Security Features

### Authentication
- **Admin Key Protection**: Simple key-based authentication
- **SSO Integration**: Enterprise-grade authentication
- **Session Management**: Secure session handling
- **Access Control**: Domain and email restrictions

### Data Protection
- **CSRF Protection**: Cross-site request forgery protection
- **Input Validation**: Secure input handling
- **SQL Injection Prevention**: Parameterized queries
- **XSS Protection**: Cross-site scripting prevention

## 📱 Mobile Responsiveness

The admin dashboard is fully responsive and works on:
- **Desktop Computers**: Full feature access
- **Tablets**: Touch-friendly interface
- **Mobile Phones**: Optimized for small screens

### Mobile Features
- **Touch Navigation**: Touch-friendly buttons and links
- **Responsive Tables**: Scrollable data tables
- **Mobile Menus**: Collapsible navigation
- **Touch Gestures**: Swipe and tap interactions

## 🚨 Troubleshooting

### Common Issues

#### Can't Access Admin Dashboard
1. Check the admin key: `?key=wedding2024`
2. Verify SSO settings if using SSO
3. Check server logs for errors

#### Navigation Links Not Working
1. Ensure all admin routes are registered
2. Check for JavaScript errors in browser console
3. Verify template files exist

#### Settings Not Saving
1. Check database permissions
2. Verify form submission
3. Check for validation errors

### Debug Mode
Enable debug mode for detailed error information:
```python
app.config['DEBUG'] = True
```

## 📈 Performance Optimization

### Database Optimization
- **Query Caching**: Cached database queries
- **Index Optimization**: Optimized database indexes
- **Connection Pooling**: Efficient database connections

### Cache Management
- **Redis Integration**: Optional Redis caching
- **Memory Caching**: In-memory cache for performance
- **Cache Invalidation**: Automatic cache cleanup

## 🔄 Updates and Maintenance

### Regular Maintenance
- **Database Cleanup**: Remove old logs and data
- **Cache Clearing**: Clear expired cache entries
- **Log Rotation**: Manage log file sizes
- **Security Updates**: Keep dependencies updated

### Monitoring
- **Error Logging**: Comprehensive error tracking
- **Performance Monitoring**: Track response times
- **User Activity**: Monitor admin usage
- **System Health**: Check system resources

## 📞 Support

For admin dashboard issues:
1. Check the troubleshooting section
2. Review server logs
3. Test with different browsers
4. Verify network connectivity

The admin dashboard provides complete control over the Wedding Gallery application with an intuitive interface and comprehensive functionality. 