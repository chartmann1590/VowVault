# Photo of the Day System

The Photo of the Day system allows administrators to select a featured photo for each day, and users can vote on it. This creates a simple, engaging way to highlight special moments from the wedding celebration.

## Overview

- **Simple Design**: One photo per day, no complex contests
- **User Voting**: Visitors can vote once per day on the featured photo
- **Admin Management**: Easy interface to select and manage photos of the day
- **History**: View recent photos of the day with voting statistics

## Features

### For Users
- View today's featured photo on the Photo of the Day page
- Vote once per day on the featured photo
- Remove your vote if you change your mind
- Browse recent photos of the day
- See voting statistics for each photo

### For Admins
- Set any photo as today's Photo of the Day
- Clear today's photo if needed
- View recent photos of the day with statistics
- Browse all available photos for selection
- See top photos by likes for easy selection

## Access

- **For Users**: Visit `/photo-of-day` to view and vote on today's photo
- **For Admins**: Access via the admin panel at `/admin/photo-of-day?key=wedding2024`

## How It Works

### Setting a Photo of the Day

1. **Access Admin Panel**: Go to `/admin/photo-of-day?key=wedding2024`
2. **Browse Photos**: View all available photos in the selection grid
3. **Select Photo**: Click on any photo to set it as today's Photo of the Day
4. **Confirm**: Confirm your selection in the popup dialog
5. **Done**: The photo is now featured for today

### User Voting

1. **Visit Page**: Users visit `/photo-of-day`
2. **View Photo**: See today's featured photo with details
3. **Vote**: Click the "Vote" button to cast your vote
4. **Remove Vote**: Click "Remove Vote" if you want to change your mind
5. **See Results**: View the current vote count and recent photos

## Database Schema

### PhotoOfDay Table
```sql
CREATE TABLE photo_of_day (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    photo_id INTEGER NOT NULL,
    date DATE NOT NULL UNIQUE,
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    is_active BOOLEAN DEFAULT TRUE,
    FOREIGN KEY (photo_id) REFERENCES photo (id)
);
```

### PhotoOfDayVote Table
```sql
CREATE TABLE photo_of_day_vote (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    photo_of_day_id INTEGER NOT NULL,
    user_identifier VARCHAR(100) NOT NULL,
    user_name VARCHAR(100) DEFAULT 'Anonymous',
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (photo_of_day_id) REFERENCES photo_of_day (id) ON DELETE CASCADE,
    UNIQUE(photo_of_day_id, user_identifier)
);
```

## API Endpoints

### User Endpoints
- `GET /photo-of-day` - View today's photo and recent photos
- `POST /api/photo-of-day/vote` - Vote for today's photo
- `POST /api/photo-of-day/unvote` - Remove your vote
- `GET /api/photo-of-day/stats` - Get voting statistics

### Admin Endpoints
- `GET /admin/photo-of-day` - Admin management interface
- `POST /admin/photo-of-day/set` - Set a photo as Photo of the Day
- `POST /admin/photo-of-day/clear` - Clear today's Photo of the Day
- `POST /admin/photo-of-day/delete/<id>` - Delete a specific Photo of the Day

## Admin Interface

### Main Dashboard
- **Today's Photo**: Display current photo of the day with details
- **Clear Button**: Remove today's photo if needed
- **Photo Selection**: Grid of all available photos for selection
- **Recent Photos**: History of recent photos of the day

### Photo Selection
- **Visual Grid**: Browse all photos with thumbnails
- **Photo Details**: See uploader, likes, and upload date
- **One-Click Selection**: Click any photo to set as today's featured photo
- **Confirmation**: Confirm selection before applying

### Statistics
- **Total Photos of the Day**: Count of all photos of the day
- **Available Photos**: Number of photos available for selection
- **Top Photos**: Photos with most likes for easy selection

## User Interface

### Today's Photo Section
- **Large Display**: Featured photo prominently displayed
- **Photo Details**: Uploader name and description
- **Voting Interface**: Vote/Unvote buttons with real-time updates
- **Vote Count**: Live display of current vote count

### Recent Photos Section
- **Photo Grid**: Display recent photos of the day
- **Date Badges**: Show when each photo was featured
- **Vote Statistics**: Display vote counts for each photo
- **Responsive Design**: Works on mobile and desktop

## Technical Details

### Voting System
- **One Vote Per User**: Users can only vote once per day
- **Real-time Updates**: Vote counts update immediately
- **Vote Removal**: Users can remove their vote if needed
- **User Tracking**: Uses user identifiers to prevent duplicate votes

### Photo Selection
- **Any Photo**: Admins can select any uploaded photo
- **Date Uniqueness**: Only one photo per day
- **Active Status**: Photos can be marked as inactive
- **Cascade Deletion**: Votes are deleted when photos are removed

### Performance
- **Database Indexes**: Optimized queries for fast performance
- **Caching**: Efficient data loading and display
- **Responsive Images**: Optimized image loading and display

## Migration

The system includes backward compatibility with the old contest-based system:

- **Legacy Tables**: Old contest tables are preserved
- **Data Migration**: Existing data is maintained
- **Gradual Transition**: Can be migrated over time

## Security

- **Admin Access**: Protected by admin key authentication
- **User Validation**: Proper user identification and validation
- **SQL Injection Protection**: Parameterized queries
- **XSS Protection**: Proper input sanitization

## Troubleshooting

### Common Issues

1. **No Photo of the Day**: Admin needs to select a photo
2. **Can't Vote**: User may have already voted
3. **Vote Not Counted**: Check user identifier and database connection
4. **Admin Access**: Verify admin key is correct

### Debug Steps

1. Check database connection and tables
2. Verify user identifiers are being set
3. Check admin authentication
4. Review server logs for errors

## Future Enhancements

- **Scheduled Photos**: Pre-schedule photos for future dates
- **Photo Categories**: Organize photos by categories
- **Advanced Analytics**: Detailed voting and engagement statistics
- **Social Sharing**: Share photos of the day on social media
- **Email Notifications**: Notify users of new photos of the day 