# Live Event Slideshow Feature

## Overview

The Live Event Slideshow is a dynamic, real-time display feature that automatically showcases all activities from your wedding celebration. It provides a beautiful, full-screen presentation with stunning visual effects and smooth transitions that updates every 15 minutes with the latest photos, guestbook entries, and messages from your guests.

## Features

### 🎬 Enhanced Slideshow Experience
- **Real-time Updates**: Automatically refreshes every 15 minutes to show the latest activities
- **Smooth Transitions**: Advanced slide effects with 3D transforms and easing animations
- **Dual Fullscreen Modes**: 
  - Browser fullscreen for complete immersion
  - Slideshow-only fullscreen for focused viewing
- **Play/Pause Controls**: Users can control the slideshow playback
- **Progress Bar**: Visual indicator showing time until next slide transition

### 🎨 Beautiful Visual Design
- **Modern Animations**: Smooth slide-in/slide-out effects with 3D rotations
- **Gradient Backgrounds**: Eye-catching gradients for different content types
- **Hover Effects**: Interactive elements with subtle animations
- **Shimmer Effects**: Elegant shimmer animations on guestbook and message slides
- **Responsive Design**: Optimized for all screen sizes and devices

### 📊 Activity Types Displayed
- **Photos & Videos**: All uploaded photos and videos from guests with zoom effects
- **Guestbook Entries**: Messages and photos from the guestbook with gradient backgrounds
- **Message Board Posts**: Messages and photos from the message board with unique styling
- **Photobooth Photos**: Special highlighting for photobooth captures

### 🎯 Enhanced User Experience
- **Visual Feedback**: Animated progress bar showing slide timing
- **Smooth Transitions**: 800ms cubic-bezier transitions for professional feel
- **Interactive Elements**: Hover effects and button animations
- **Auto-refresh Indicator**: Shows when the content was last updated with pulse animation

## How to Use

### For Guests
1. Navigate to the "🎬 Live Slideshow" link in the main navigation
2. The slideshow will automatically start displaying recent activities with smooth transitions
3. Use the play/pause button to control the slideshow
4. Click the fullscreen button (⛶) for browser fullscreen mode
5. Click the slideshow fullscreen button (🎬) for slideshow-only fullscreen
6. Watch the progress bar at the bottom to see timing for next slide
7. The page automatically refreshes every 15 minutes

### For Event Organizers
- The slideshow is perfect for displaying on large screens during the reception
- The dual fullscreen modes provide flexibility for different display scenarios
- Advanced animations create a professional, engaging presentation
- The slideshow automatically shows the most recent activities without manual intervention

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

### Default Settings
- **slideshow_interval**: 5000ms (5 seconds between slides)
- **transition_effect**: 'fade' (smooth fade transitions)
- **show_photos**: 'true' (display photos in slideshow)
- **show_guestbook**: 'true' (display guestbook entries)
- **show_messages**: 'true' (display message board posts)
- **auto_refresh**: 'true' (automatically refresh content)
- **refresh_interval**: 900000ms (15 minutes)
- **max_activities**: 50 (maximum activities to display)
- **time_range_hours**: 24 (hours of content to show)

### Animation Features
- **Slide Transitions**: 3D transforms with scale and rotation effects
- **Content Animations**: Staggered fade-in animations for slide content
- **Progress Bar**: Smooth linear progress indicator
- **Hover Effects**: Scale and shadow animations on interactive elements
- **Shimmer Effects**: Continuous shimmer animations on special content types

### Fullscreen Modes
1. **Browser Fullscreen**: Uses native browser fullscreen API
2. **Slideshow Fullscreen**: Custom fullscreen mode that maximizes the slideshow area

### Responsive Design
- **Desktop**: Full feature set with all animations
- **Tablet**: Optimized layout with reduced padding
- **Mobile**: Simplified controls and touch-friendly interface

## API Endpoints

### GET /slideshow
Main slideshow page with enhanced visual effects

### GET /api/slideshow/activities
Returns recent activities for slideshow display

### GET/POST /api/slideshow/settings
Manages slideshow configuration settings

## Performance Optimizations
- **Cached Queries**: Database queries are cached for 5 minutes
- **Efficient Animations**: Hardware-accelerated CSS transforms
- **Lazy Loading**: Content loads progressively for smooth experience
- **Memory Management**: Proper cleanup of intervals and event listeners

## Browser Compatibility
- **Modern Browsers**: Full support for all features
- **CSS Grid/Flexbox**: Responsive layout system
- **CSS Animations**: Hardware-accelerated transitions
- **Fullscreen API**: Native browser fullscreen support 