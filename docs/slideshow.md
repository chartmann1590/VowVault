# Live Event Slideshow Feature

## Overview

The Live Event Slideshow is a dynamic, real-time display feature that automatically showcases all activities from your wedding celebration. It provides a beautiful, full-screen presentation that updates every 15 minutes with the latest photos, guestbook entries, and messages from your guests.

## Features

### 🎬 Automatic Slideshow
- **Real-time Updates**: Automatically refreshes every 15 minutes to show the latest activities
- **Smooth Transitions**: Elegant fade transitions between slides
- **Full-screen Mode**: Perfect for displaying on TVs or projectors during events
- **Play/Pause Controls**: Users can control the slideshow playback

### 📊 Activity Types Displayed
- **Photos & Videos**: All uploaded photos and videos from guests
- **Guestbook Entries**: Messages and photos from the guestbook
- **Message Board Posts**: Messages and photos from the message board
- **Photobooth Photos**: Special highlighting for photobooth captures

### 🎨 Beautiful Presentation
- **Modern Design**: Gradient backgrounds and elegant typography
- **Responsive Layout**: Works perfectly on all devices
- **Activity Statistics**: Live counters showing today's activity totals
- **Auto-refresh Indicator**: Shows when the content was last updated

## How to Use

### For Guests
1. Navigate to the "🎬 Live Slideshow" link in the main navigation
2. The slideshow will automatically start displaying recent activities
3. Use the play/pause button to control the slideshow
4. Click the fullscreen button for an immersive experience
5. The page automatically refreshes every 15 minutes

### For Event Organizers
- The slideshow is perfect for displaying on large screens during the reception
- It automatically shows the most recent activities without manual intervention
- The fullscreen mode provides a professional presentation

## Technical Details

### Database Schema

#### SlideshowSettings Table
```sql
CREATE TABLE slideshow_settings (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    key VARCHAR(100) UNIQUE NOT NULL,
    value TEXT NOT NULL,
    updated_at DATETIME DEFAULT CURRENT_TIMESTAMP
);
```

#### SlideshowActivity Table
```sql
CREATE TABLE slideshow_activity (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    activity_type VARCHAR(50) NOT NULL,
    content_id INTEGER NOT NULL,
    content_summary TEXT,
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    is_active BOOLEAN DEFAULT TRUE
);
```

### API Endpoints

#### GET /slideshow
- **Purpose**: Main slideshow page
- **Response**: Rendered HTML template with slideshow interface

#### GET /api/slideshow/activities
- **Purpose**: Get recent activities for slideshow
- **Parameters**: 
  - `hours` (optional): Time range in hours (default: 24)
- **Response**: JSON with activities array and metadata

#### GET /api/slideshow/settings
- **Purpose**: Get current slideshow settings
- **Response**: JSON with all settings

#### POST /api/slideshow/settings
- **Purpose**: Update slideshow settings
- **Body**: JSON with setting key-value pairs
- **Response**: Success status

### Configuration Settings

| Setting | Default | Description |
|---------|---------|-------------|
| `slideshow_interval` | 5000 | Time between slides in milliseconds |
| `transition_effect` | fade | Transition effect (fade/slide) |
| `show_photos` | true | Include photos in slideshow |
| `show_guestbook` | true | Include guestbook entries |
| `show_messages` | true | Include message board posts |
| `auto_refresh` | true | Enable automatic content refresh |
| `refresh_interval` | 900000 | Refresh interval in milliseconds (15 min) |
| `max_activities` | 50 | Maximum activities to display |
| `time_range_hours` | 24 | Time range for activities |

## Installation & Setup

### 1. Database Migration
The slideshow tables are automatically created when the migration script runs:

```bash
python migration.py
```

### 2. File Structure
```
app/
├── models/
│   └── slideshow.py          # Database models
├── views/
│   └── slideshow.py          # Routes and API endpoints
templates/
└── slideshow.html            # Slideshow page template
```

### 3. Navigation Integration
The slideshow link is automatically added to both desktop and mobile navigation menus.

## Customization

### Styling
The slideshow uses custom CSS with:
- Gradient backgrounds
- Glassmorphism effects
- Smooth animations
- Responsive design

### Content Filtering
You can customize what content appears by modifying the API endpoint in `app/views/slideshow.py`.

### Timing
Adjust the refresh intervals and slide timing through the settings API or by modifying the default values.

## Browser Compatibility

- ✅ Chrome/Chromium (recommended)
- ✅ Firefox
- ✅ Safari
- ✅ Edge
- ⚠️ Internet Explorer (limited support)

## Mobile Support

The slideshow is fully responsive and works well on:
- Smartphones
- Tablets
- Mobile browsers

## Performance Considerations

- **Caching**: Settings are cached for 5 minutes
- **Optimized Queries**: Database queries use indexes for performance
- **Lazy Loading**: Content loads progressively
- **Memory Management**: Old slides are cleaned up automatically

## Troubleshooting

### Common Issues

1. **Slideshow not updating**
   - Check that auto-refresh is enabled
   - Verify the refresh interval setting
   - Check browser console for errors

2. **Images not displaying**
   - Ensure upload directories exist
   - Check file permissions
   - Verify image paths are correct

3. **Performance issues**
   - Reduce the number of activities displayed
   - Increase the refresh interval
   - Check database performance

### Debug Mode
Enable browser developer tools to see:
- API request/response logs
- JavaScript errors
- Network activity

## Future Enhancements

Potential improvements for future versions:
- Custom transition effects
- Background music support
- Social media integration
- Advanced filtering options
- Admin controls for content curation
- Export slideshow as video
- Multiple slideshow themes

## Support

For issues or questions about the slideshow feature:
1. Check the browser console for errors
2. Verify database connectivity
3. Test with different browsers
4. Review the API endpoints for proper responses 