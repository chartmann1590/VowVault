# 📸 Photo of the Day Voting System

The Photo of the Day feature allows wedding guests to vote on daily featured photos, creating an engaging and interactive experience for your wedding gallery.

## ✨ Features

### For Guests
- **Daily Featured Photos**: Admins can select a photo to be featured each day
- **Voting System**: Guests can vote once per day for the featured photo
- **Vote Tracking**: See how many votes each photo has received
- **Recent History**: View photos of the day from the past week
- **User-Friendly Interface**: Clean, intuitive voting interface with real-time updates

### For Admins
- **Photo Selection**: Choose any uploaded photo to be featured on any date
- **Candidate Management**: Mark photos as candidates for future selection
- **Vote Statistics**: View voting statistics and engagement metrics
- **Date Management**: Set photos for past, present, or future dates
- **Easy Management**: Simple admin interface for managing all Photo of the Day content

## 🚀 Getting Started

### 1. Run the Migration
First, run the Photo of the Day migration to create the necessary database tables:

```bash
python migrate_photo_of_day.py
```

### 2. Access the Feature
- **For Guests**: Navigate to "📸 Photo of the Day" in the main navigation
- **For Admins**: Access via the admin panel at `/admin/photo-of-day?key=wedding2024`

## 📱 User Experience

### Guest Voting Flow
1. **Visit Photo of the Day Page**: Click "📸 Photo of the Day" in the navigation
2. **View Today's Photo**: See the featured photo with details and uploader information
3. **Vote**: Click the "Vote for this Photo!" button to cast your vote
4. **See Results**: View the updated vote count and recent photos of the day
5. **Change Vote**: Click "Remove Vote" to change your mind (one vote per day)

### Admin Management Flow
1. **Access Admin Panel**: Go to `/admin/photo-of-day?key=wedding2024`
2. **Select Photo**: Choose from all uploaded photos in the dropdown
3. **Choose Date**: Pick which date this photo should be featured
4. **Preview**: See a preview of your selection before confirming
5. **Confirm**: Click "Set as Photo of the Day" to save
6. **Manage**: View, edit, or delete existing photos of the day

## 🛠️ Technical Details

### Database Schema

#### PhotoOfDay Table
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

#### PhotoOfDayVote Table
```sql
CREATE TABLE photo_of_day_vote (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    photo_of_day_id INTEGER NOT NULL,
    user_identifier VARCHAR(100) NOT NULL,
    user_name VARCHAR(100) DEFAULT 'Anonymous',
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (photo_of_day_id) REFERENCES photo_of_day (id),
    UNIQUE(photo_of_day_id, user_identifier)
);
```

#### PhotoOfDayCandidate Table
```sql
CREATE TABLE photo_of_day_candidate (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    photo_id INTEGER NOT NULL,
    date_added DATE NOT NULL,
    is_selected BOOLEAN DEFAULT FALSE,
    selected_date DATE,
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (photo_id) REFERENCES photo (id)
);
```

### API Endpoints

#### Guest Endpoints
- `GET /photo-of-day` - View today's photo and recent history
- `POST /api/photo-of-day/vote` - Vote for today's photo
- `POST /api/photo-of-day/unvote` - Remove your vote
- `GET /api/photo-of-day/stats` - Get voting statistics

#### Admin Endpoints
- `GET /admin/photo-of-day` - Admin management interface
- `POST /admin/photo-of-day/select` - Select a photo for a specific date
- `POST /admin/photo-of-day/delete/{id}` - Delete a photo of the day
- `POST /admin/photo-of-day/add-candidate` - Add a photo as a candidate

## 🎨 Customization

### Styling
The Photo of the Day feature uses the same design system as the rest of the application:
- **Colors**: Pink theme (`#e91e63`) for voting buttons
- **Typography**: Inter font family for consistency
- **Layout**: Responsive grid system for mobile and desktop
- **Animations**: Smooth transitions for vote interactions

### Templates
- `templates/photo_of_day.html` - Main guest interface
- `templates/admin_photo_of_day.html` - Admin management interface

## 🔧 Configuration

### Admin Access
The admin interface is protected by the same key system as other admin features:
- Default key: `wedding2024`
- Access URL: `/admin/photo-of-day?key=wedding2024`

### Database Configuration
The feature works with the existing database configuration:
- **SQLite**: Default local development
- **PostgreSQL**: Production deployments
- **Docker**: Containerized deployments

## 📊 Analytics

### Available Statistics
- **Total Votes**: Number of votes cast for each photo
- **Unique Voters**: Number of different users who voted
- **Daily Engagement**: Votes per day tracking
- **Photo Performance**: Which photos receive the most votes

### Admin Dashboard Metrics
- Total Photos of the Day created
- Number of candidate photos
- Voting engagement statistics
- Recent activity overview

## 🚨 Troubleshooting

### Common Issues

#### Migration Errors
```bash
# If migration fails, check database permissions
chmod 755 instance/
chmod 644 instance/wedding_photos.db
```

#### Voting Issues
- **"User identifier required"**: Ensure cookies are enabled
- **"Already voted"**: Users can only vote once per day
- **"No photo of the day"**: Admin needs to select a photo for today

#### Admin Access Issues
- **"Unauthorized"**: Check admin key in URL parameter
- **"Photo not found"**: Ensure photo exists in database
- **"Date already exists"**: Only one photo per date allowed

### Debug Steps
1. **Check Database**: Verify tables exist with `sqlite3 instance/wedding_photos.db`
2. **Check Logs**: Review application logs for errors
3. **Test Migration**: Run `python migrate_photo_of_day.py` again
4. **Verify Routes**: Check that blueprints are registered correctly

## 🔮 Future Enhancements

### Planned Features
- **Automatic Selection**: AI-powered photo selection based on engagement
- **Voting Campaigns**: Special voting events for specific dates
- **Photo Categories**: Different types of photos (couple, family, friends)
- **Social Sharing**: Share photos of the day on social media
- **Email Notifications**: Notify users when new photos are selected
- **Voting Rewards**: Special badges or recognition for active voters

### Integration Ideas
- **Wedding Timeline**: Integrate with wedding event timeline
- **Guest Engagement**: Track guest participation metrics
- **Photo Stories**: Create narratives around featured photos
- **Memory Book**: Compile photos of the day into a keepsake book

## 📚 Related Documentation

- **[Features Overview](features.md)** - Complete feature breakdown
- **[Installation Guide](installation.md)** - Setup and deployment
- **[Admin Guide](admin.md)** - Admin panel documentation
- **[API Reference](api.md)** - Technical API documentation

---

**Made with ❤️ for your special day**

*Part of the VowVault Wedding Photo Gallery System* 