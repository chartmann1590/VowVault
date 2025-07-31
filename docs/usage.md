# 📱 Usage Guide

## For Wedding Guests

### 1. Visit the Gallery
- Scan the QR code or visit the URL
- View the welcome message
- Choose to sign the guestbook, post a message, or enter the gallery

### 2. Upload Photos/Videos
- Click "Upload Photo/Video"
- Select your photo or video (videos max 15 seconds, files max 50MB)
- Add your name (optional)
- Add a description (optional)
- Add tags (optional) - e.g., "ceremony, reception, dance" (comma-separated)
- Click "Upload"

### 3. Search and Filter Photos
- **Collapsible Interface:** The search and filter section is collapsed by default to save space
- **Expand:** Click the "Search & Filter" header or the toggle button to expand the search options
- **Search:** Use the search bar to find photos by uploader name, description, or tags
- **Media Type Filter:** Filter by All Media, Photos Only, Videos Only, or Photobooth Only
- **Tag Filter:** Filter by specific tags using the tag dropdown
- **Apply Filters:** Click "Apply Filters" to see results
- **Clear All:** Click "Clear All" to reset filters
- **Tags:** Tags are displayed on photo cards for easy identification

### 4. Use Virtual Photobooth
- Click "Virtual Photobooth" in navigation or from the welcome screen
- Allow camera access when prompted
- Position yourself in the frame with the wedding border overlay
- Click "Take Photo" (3-second countdown)
- Download the photo or upload it directly to the gallery
- When uploading, add your name, description, and tags (optional)

### 5. Interact with Photos/Videos
- Click any photo or video to view details
- Click the heart to like
- Leave comments with your name
- Videos play with controls and show duration

### 6. Post on Message Board
- Click "Message Board" in navigation
- Click "Leave a Message"
- Enter your name (optional)
- Write your message
- Add a photo (optional)
- Submit your message
- Like and comment on other messages

### 7. Sign the Guestbook
- Click "Guestbook" in navigation
- Click "Sign the Guestbook"
- Enter your name and location (optional)
- Write your message
- Add a photo (optional)
- Submit your entry

### 8. Install as PWA (Mobile)
- **Android/Chrome:** Menu → Add to Home screen
- **iPhone/Safari:** Share button → Add to Home Screen
- **Other browsers:** Look for install options in browser menu

### 9. Enable Notifications (Mobile)
- **Access:** Open the mobile hamburger menu (☰)
- **Toggle:** Tap "Enable Notifications" to turn on/off
- **Permission:** Grant browser notification permission when prompted
- **Status:** Icon shows 🔔 when enabled, 🔕 when disabled
- **Smart:** Only get notified about others' interactions with your content

## For Administrators

### 1. Access Admin Panel
- Visit `/admin?key=your-key`
- View comprehensive statistics including photobooth usage
- Manage photos, videos, messages, and guestbook entries

### 2. Batch Download All Content
- Click "Download All Content" button
- Automatically downloads a ZIP file containing:
  - All photos organized by type (photos/, videos/, photobooth/, etc.)
  - All video thumbnails
  - All guestbook and message photos
  - Complete database export as JSON
  - Photobooth border images

### 3. System Reset
- Click "System Reset" button for complete data wipe
- Must type "RESET EVERYTHING" to confirm
- Deletes all database records and uploaded files
- Returns system to fresh state

### 4. Configure Virtual Photobooth
- Upload a custom border image (PNG with transparency recommended)
- Recommended size: 1280x720px or 16:9 aspect ratio
- Test the photobooth to ensure proper overlay

### 5. PWA Debug Tools
- Click "PWA Debug" button in admin panel
- View PWA requirements status (HTTPS, manifest, service worker, icons)

### 6. Configure Timezone Settings
- Navigate to "Timezone Settings" in admin dashboard
- Select your preferred timezone from the dropdown
- View real-time preview of current time in selected timezone
- Save settings to see all admin dates/times in your local timezone
- Affects photo upload dates, guestbook timestamps, message times, and system logs
- Check connection details and user agent information
- Get troubleshooting solutions for self-signed certificates
- Access quick links to view manifest and service worker files

### 6. Email Configuration
- Configure SMTP settings for email photo uploads
- Set up email monitoring for automatic photo processing
- Test email functionality with confirmation messages

### 7. Immich Server Sync
- Configure Immich server settings
- Enable sync for different content types
- Monitor sync status and logs
- Manage album organization

### 8. Content Management
- Delete inappropriate content
- Hide/show messages without deletion
- Edit guestbook entries
- Manage photo attachments

### 9. QR Code Generation
- Create custom QR code PDFs
- Set wedding couple names and messages
- Include email upload instructions
- Download and print for distribution

## Mobile Experience

### Responsive Design
- Optimized for all screen sizes
- Touch-friendly interface
- Fast loading on mobile networks
- PWA installation support

### PWA Features
- Native app experience
- Offline functionality
- Home screen installation
- App shortcuts for quick access

### Notification System
- **Mobile Toggle:** Easy enable/disable in hamburger menu
- **Smart Notifications:** Only for others' interactions with your content
- **Browser Integration:** Native notifications with app branding
- **Permission Management:** One-time setup with browser permission
- **Session Persistence:** Settings saved across browser sessions

## Best Practices

### For Guests
1. **Photo Quality:** Upload high-quality photos for best results
2. **Video Length:** Keep videos under 15 seconds for optimal performance
3. **Descriptions:** Add meaningful descriptions to help identify photos
4. **Tags:** Use descriptive tags like "ceremony", "reception", "dance" to help others find photos
5. **Comments:** Leave thoughtful comments to share memories
6. **PWA Installation:** Install the app for quick access
7. **Notifications:** Enable notifications to stay connected with your content
8. **Interaction:** Like and comment on others' photos to share appreciation
9. **Search:** Use the search and filter features to find specific photos quickly

### For Administrators
1. **Regular Backups:** Use the batch download feature regularly
2. **Content Moderation:** Monitor and moderate content as needed
3. **Email Monitoring:** Check email processing logs regularly
4. **PWA Testing:** Test PWA functionality on multiple devices
5. **Performance Monitoring:** Monitor upload sizes and system performance 