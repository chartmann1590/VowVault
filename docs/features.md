# ✨ Features

## For Guests

### 📸 Easy Photo/Video Upload
No login required, just upload and share! Supports photos and videos up to 50MB, with videos limited to 15 seconds for optimal performance.

**Supported Formats:**
- **Photos:** PNG, JPG, JPEG, GIF, WEBP
- **Videos:** MP4, MOV, AVI (max 15 seconds)

### 🔍 Search & Tagging
Find photos quickly with powerful search and tagging features. Organize and discover memories with ease.

**Search Features:**
- **Text Search:** Search by uploader name, description, or tags
- **Media Type Filter:** Filter by photos, videos, or photobooth images
- **Tag Filter:** Filter by specific tags like "ceremony", "reception", "dance"
- **Real-time Results:** Instant search results as you type
- **Mobile Optimized:** Responsive search interface for all devices

**Tagging System:**
- **Custom Tags:** Add tags when uploading (e.g., "ceremony", "reception", "cake")
- **Tag Display:** Tags shown on photo cards for easy identification
- **Tag Suggestions:** Common wedding tags available in dropdown
- **Comma-separated:** Multiple tags per photo (e.g., "ceremony, dance, family")
- **Search Integration:** Tags included in search results

**Example Tags:**
- `ceremony` - Wedding ceremony photos
- `reception` - Reception and party photos
- `dance` - Dancing and celebration moments
- `cake` - Cake cutting and dessert photos
- `family` - Family group photos
- `friends` - Friend group photos
- `decorations` - Wedding decorations and venue
- `food` - Catering and meal photos

### 📧 Email Photo Upload
Send photos directly via email to automatically add them to the gallery. Perfect for guests who prefer email over web uploads.

**How it works:**
1. Attach photos to an email
2. Send to your configured email address
3. Photos are automatically added to the gallery
4. You receive a confirmation email with a link

### 🤳 Virtual Photobooth
Take photos with custom wedding borders using your device camera. Create beautiful memories with personalized overlays.

**Features:**
- Real-time camera preview
- Custom wedding border overlays
- 3-second countdown timer
- Download or upload directly to gallery
- Works on all mobile devices

### ❤️ Like Photos/Videos
Show appreciation for beautiful moments with a simple heart click. Track which photos are most loved by your guests.

### 💬 Leave Comments
Share memories and messages on photos and videos. Add your name and leave heartfelt comments for the couple.

### 🔔 Smart Notifications
Get notified when someone likes or comments on your photos and messages. Stay connected with your wedding memories.

**Notification Features:**
- **Photo Notifications:** Get alerted when someone likes or comments on your photos
- **Message Notifications:** Receive notifications for message interactions
- **Smart Filtering:** Only get notified about others' actions, not your own
- **Mobile Toggle:** Easy enable/disable in the mobile hamburger menu
- **Browser Integration:** Uses native browser notifications with app icons
- **Personalized Messages:** Shows actual user names in notifications

### 💌 Message Board
Post messages with optional photos that everyone can see, like, and comment on. A digital guestbook for sharing thoughts and memories.

**Features:**
- Text messages with optional photos
- Like and comment on messages
- Real-time updates
- Photo attachments supported

### 📖 Virtual Guestbook
Sign a digital guestbook with wishes and optional photos. Leave lasting memories for the couple.

**Information collected:**
- Your name (optional)
- Your location (optional)
- Your message
- Optional photo attachment

### 📱 Mobile Responsive
Works perfectly on all devices - phones, tablets, and desktops. Optimized for touch interfaces and mobile browsing.

### 📱 Progressive Web App (PWA)
Install as a native app on mobile devices for quick access. Get the full app experience without downloading from app stores.

**PWA Features:**
- Native app experience

### 🏆 Photo of the Day
Vote for daily featured photos and see which moments are most loved by your guests. Admins can select photos to be featured each day, and guests can vote once per day. The system now includes automatic candidate selection based on photo popularity.

**Voting Features:**
- **Daily Featured Photos:** Admins select photos to be featured each day
- **One Vote Per Day:** Each guest can vote once per day for the featured photo
- **Vote Tracking:** See how many votes each photo has received
- **Recent History:** View photos of the day from the past week
- **Real-time Updates:** Vote counts update instantly
- **User-Friendly Interface:** Clean, intuitive voting interface

**Guest Experience:**
- Visit the "📸 Photo of the Day" page from the main navigation
- View today's featured photo with details and uploader information
- Click "Vote for this Photo!" to cast your vote
- See the updated vote count and recent photos of the day
- Change your mind by clicking "Remove Vote" (one vote per day)

**Recent Photos:**
- View photos of the day from the past 7 days
- See vote counts and uploader information
- Browse through recent highlights
- Offline support
- Fast loading
- Custom app icons
- App shortcuts

**Automatic Candidate System:**
- **Smart Selection:** Photos with enough likes automatically become candidates
- **Configurable Threshold:** Admins can adjust the minimum likes required (default: 3)
- **Popularity-Based:** Most-liked photos are prioritized for selection
- **Visual Indicators:** Auto-candidates marked with orange "Auto" labels
- **Manual Override:** Admins can still manually select any photo

### 🎉 Welcome Modal
Greet guests with a personalized message and instructions. Set the tone for your wedding gallery experience.

## For Admins

### 🔐 Admin Dashboard
Secure admin area with simple key authentication. Manage your wedding gallery with comprehensive tools.

**Access:** `/admin?key=your-key`

### 📊 Statistics
View comprehensive statistics including:
- Total photos and videos
- Total likes and comments
- Message board posts
- Guestbook entries
- Photobooth usage

### 📧 Email Photo Upload Configuration
Configure email settings to allow guests to email photos directly to the gallery.

**Settings include:**
- SMTP server configuration
- Email monitoring settings
- Automatic photo processing
- Confirmation emails

### 🔄 Immich Server Sync
Automatically sync all uploads to your own Immich server for backup and organization.

**Sync options:**
- Photos and videos
- Guestbook photos
- Message board photos
- Photobooth photos
- Custom album organization

### 📱 PWA Debug Tools
Monitor PWA installation status and troubleshoot issues with comprehensive debugging tools.

**Debug features:**
- PWA requirements check
- Installation status monitoring
- Troubleshooting guides
- Connection analysis

### 🔔 Notification System
The notification system enhances user engagement by alerting users when others interact with their content.

**System features:**
- **Smart Filtering:** Only notifies about others' actions
- **Mobile Integration:** Easy toggle in hamburger menu
- **Browser Notifications:** Native notification support
- **Session Persistence:** Settings saved across sessions
- **Personalized Messages:** Shows actual user names
- **App Branding:** Uses VowVault icons and styling

### 🗑️ Content Management
Delete inappropriate photos, messages, or guestbook entries. Maintain quality control over your gallery.

### 👁️ Hide/Show Messages
Hide inappropriate messages without deleting them. Perfect for temporary moderation.

### ✏️ Edit Guestbook
Modify guestbook entries when needed. Correct typos or update information.

### 🖼️ Media Management
View and manage photos attached to messages and guestbook entries. Organize your media effectively.

### 🎨 Photobooth Border Upload
Upload custom borders for the virtual photobooth. Personalize the experience with your wedding theme.

**Requirements:**
- PNG format with transparency
- Recommended size: 1280x720px
- 16:9 aspect ratio preferred

### 📄 QR Code Generator
Create beautiful PDFs with QR codes for easy sharing. Print and distribute at your wedding.

**Customizable content:**
- Wedding couple names
- Custom messages
- Email instructions
- QR code styling

### ✏️ Customizable Content
Edit welcome messages, modal settings, and QR code content. Personalize the experience for your guests.

### 💾 Batch Download
Download all gallery content (photos, videos, data) as a comprehensive ZIP file.

**Includes:**
- All photos organized by type
- Video thumbnails
- Guestbook and message photos
- Complete database export
- Photobooth borders

### 🏆 Photo of the Day Management
Select and manage daily featured photos that guests can vote on. Create engaging content and track guest engagement. The system now includes automatic candidate selection based on photo popularity.

**Management Features:**
- **Photo Selection:** Choose any uploaded photo to be featured on any date
- **Automatic Candidate System:** Photos with enough likes automatically become candidates
- **Likes Threshold Configuration:** Adjust the minimum likes required for auto-candidates (1-50)
- **Auto-Candidate Management:** View and manage photos eligible for automatic selection
- **Date Management:** Set photos for past, present, or future dates
- **Candidate System:** Mark photos as candidates for future selection
- **Vote Statistics:** View voting statistics and engagement metrics
- **Easy Interface:** Simple admin interface for managing all Photo of the Day content
- **Photo Preview:** Preview selected photos before confirming
- **Bulk Management:** View all photos of the day in one place

**Admin Workflow:**
1. Access Photo of the Day management at `/admin/photo-of-day?key=wedding2024`
2. Configure auto-candidates by setting the likes threshold (default: 3)
3. View photos that meet the likes threshold for automatic selection
4. Manually trigger adding auto-candidates or add them individually
5. Select a photo from candidates or all uploaded photos
6. Choose which date this photo should be featured
7. Preview your selection before confirming
8. Click "Set as Photo of the Day" to save
9. View, edit, or delete existing photos of the day

**Auto-Candidate Features:**
- **Threshold Control:** Real-time adjustment of likes threshold (1-50)
- **Eligible Photos Display:** See all photos that meet the current threshold
- **Manual Trigger:** "Add Auto-Candidates Now" button for immediate processing
- **Visual Distinction:** Auto-candidates marked with orange "Auto" labels
- **Duplicate Prevention:** System prevents adding the same photo twice
- **Popularity Sorting:** Photos sorted by likes count for easy selection

**Statistics Available:**
- Total Photos of the Day created
- Number of candidate photos (manual + auto)
- Number of auto-candidate eligible photos
- Current likes threshold setting
- Voting engagement statistics
- Recent activity overview
- Vote counts per photo
- Unique voter tracking

### 🔄 System Reset
Complete system reset with confirmation to start fresh. Perfect for testing or starting over.

**Safety features:**
- Confirmation required
- "RESET EVERYTHING" must be typed
- Complete data wipe
- Fresh start capability 