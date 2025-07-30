# Wedding Gallery Features

## Core Features

### Navigation System
- **Responsive Design**: Optimized for both desktop and mobile devices
- **Dropdown Menus**: Desktop navigation uses organized dropdown menus to reduce clutter
- **Mobile Optimization**: Full-width mobile menu with improved spacing and readability
- **Touch-Friendly**: Large touch targets for mobile devices
- **Smooth Animations**: Smooth transitions and hover effects
- **Accessibility**: Proper ARIA labels and keyboard navigation support

### Photo & Video Gallery
- **Upload System**: Guests can upload photos and videos directly through the web interface
- **Email Upload**: Alternative email-based upload system for convenience
- **Video Support**: MP4, MOV, AVI, WEBM formats with automatic thumbnails
- **Photo Support**: PNG, JPG, JPEG, GIF, WEBP formats
- **File Size Limits**: 50MB maximum file size
- **Video Duration**: 15-second limit for videos
- **Tags & Descriptions**: Add metadata to help organize and find photos
- **Like System**: Guests can like their favorite photos
- **Comments**: Leave comments on photos
- **Responsive Design**: Works perfectly on mobile and desktop
- **Collapsible Search**: Search and filter interface collapses by default to save space
- **Advanced Filtering**: Filter by media type, tags, and search terms
- **Smooth Animations**: Smooth expand/collapse animations for search interface

### Guestbook System
- **Digital Guestbook**: Leave messages and well-wishes
- **Photo Attachments**: Add photos to guestbook entries
- **Location Tracking**: Optional location sharing
- **Admin Management**: Hide/delete inappropriate entries
- **Real-time Updates**: New entries appear immediately

### Message Board
- **Public Messages**: Share thoughts and memories
- **Photo Attachments**: Add photos to messages
- **Like System**: Like messages from other guests
- **Comments**: Reply to messages
- **Admin Controls**: Moderate content as needed

### Virtual Photobooth
- **Camera Integration**: Take photos directly in the browser
- **Custom Borders**: Upload your wedding border image
- **Download & Upload**: Save photos locally or upload to gallery
- **Mobile Optimized**: Works great on phones and tablets

### Admin Dashboard
- **Photo Management**: Delete, hide, and organize photos
- **Content Moderation**: Manage guestbook and messages
- **System Settings**: Configure all features
- **Statistics**: View usage and engagement metrics
- **Batch Operations**: Download all content at once

## Advanced Features

### Email Integration
- **Email Monitor**: Automatically process photos sent via email
- **SMTP Configuration**: Custom email server setup
- **IMAP Support**: Monitor email folders for uploads
- **Auto-processing**: Photos automatically added to gallery

### Immich Server Sync
- **Automatic Sync**: Uploads automatically sync to your Immich server
- **Album Organization**: Photos organized in dedicated albums
- **Metadata Preservation**: Uploader names and descriptions included
- **Selective Sync**: Choose what types of content to sync
- **Error Handling**: Robust error handling and logging

### SSO Authentication
- **Multiple Providers**: Google, Azure, Okta, Custom OAuth
- **Domain Restrictions**: Limit access to specific domains
- **Email Whitelist**: Allow specific email addresses
- **Fallback Support**: Admin key still works as backup
- **Secure Sessions**: Encrypted session management

### Push Notifications
- **Real-time Alerts**: Get notified of new uploads
- **Browser Notifications**: Works on all modern browsers
- **User Management**: Track notification subscribers
- **Admin Controls**: Send custom notifications
- **PWA Support**: Progressive Web App capabilities

### QR Code System
- **Custom QR Codes**: Personalized with your wedding details
- **PDF Generation**: Download QR codes for printing
- **Multiple Formats**: Different sizes and styles
- **Easy Sharing**: Share QR codes with guests

### Welcome Modal
- **Customizable Welcome**: Personalized welcome message
- **Photo Display**: Show couple photo
- **Instructions**: Custom instructions for guests
- **One-time Display**: Show only once per session

### Database Optimization
- **Performance Indexes**: Optimized for thousands of photos
- **Caching System**: Intelligent caching for fast loading
- **Maintenance Tools**: Database cleanup and optimization
- **Statistics**: Detailed usage analytics

### Photo of the Day
- **Daily Selection**: Choose a featured photo each day
- **Voting System**: Guests can vote on candidates
- **Admin Selection**: Manual override capability
- **Archive**: Historical photo of the day records

### CAPTCHA Spam Prevention
- **Math Challenges**: Simple arithmetic problems for verification
- **Configurable Protection**: Enable/disable for different areas
- **User-friendly Design**: Matches your wedding theme
- **Security Features**: 5-minute expiration, one-time use
- **Admin Controls**: Enable/disable from admin panel
- **Free & Self-hosted**: No external dependencies or costs

## Technical Features

### Progressive Web App (PWA)
- **Offline Support**: Works without internet connection
- **App-like Experience**: Install on mobile devices
- **Push Notifications**: Real-time updates
- **Background Sync**: Automatic data synchronization

### Security Features
- **File Validation**: Secure file upload handling
- **XSS Protection**: Cross-site scripting prevention
- **CSRF Protection**: Cross-site request forgery protection
- **Input Sanitization**: Clean user input handling
- **Session Security**: Encrypted session management

### Performance Features
- **Image Optimization**: Automatic thumbnail generation
- **Lazy Loading**: Images load as needed
- **Caching**: Intelligent caching for fast performance
- **CDN Ready**: Works with content delivery networks
- **Mobile Optimized**: Fast loading on mobile devices

### Developer Features
- **Docker Support**: Easy deployment with Docker
- **Environment Configuration**: Flexible configuration system
- **Logging**: Comprehensive logging for debugging
- **Error Handling**: Graceful error handling
- **API Endpoints**: RESTful API for integrations

## Installation & Setup

### Quick Start
1. **Docker Deployment**: `docker-compose up -d`
2. **Local Setup**: Python virtual environment
3. **Configuration**: Environment variables and admin panel
4. **Customization**: Upload borders, QR codes, welcome messages

### Configuration Options
- **Email Settings**: SMTP/IMAP configuration
- **Immich Integration**: Server URL and API keys
- **SSO Setup**: OAuth provider configuration
- **CAPTCHA Settings**: Spam prevention configuration
- **QR Code Customization**: Personalized QR codes
- **Welcome Modal**: Custom welcome experience

### Maintenance
- **Database Optimization**: Regular maintenance tools
- **Content Management**: Admin tools for moderation
- **Backup System**: Export all content
- **Monitoring**: Usage statistics and logs

## User Experience

### Guest Features
- **Simple Upload**: Drag-and-drop or click to upload
- **Mobile Friendly**: Works perfectly on phones
- **Fast Loading**: Optimized for quick access
- **Intuitive Interface**: Easy to use for all ages
- **Real-time Updates**: See new content immediately

### Admin Features
- **Comprehensive Dashboard**: All controls in one place
- **Bulk Operations**: Manage multiple items at once
- **Content Moderation**: Easy content management
- **System Monitoring**: Track usage and performance
- **Customization**: Extensive customization options

This wedding gallery system provides a complete solution for sharing and managing wedding photos and memories, with advanced features for security, performance, and user experience. 