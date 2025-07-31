# 📸 Photo of the Day Contest System

The Photo of the Day Contest feature allows wedding guests to vote on multiple daily photo candidates, creating an engaging and interactive experience for your wedding gallery. The system now supports multiple photos per day with voting and winner selection.

## ✨ Features

### For Guests
- **Daily Photo Contests**: Multiple photos compete each day for the title of Photo of the Day
- **Voting System**: Guests can vote once per contest for their favorite photo
- **Real-time Results**: See vote counts update in real-time
- **Contest Status**: View whether voting is open or closed
- **Winner Display**: See which photo won each contest
- **Recent Winners**: View winners from past contests
- **User-Friendly Interface**: Clean, intuitive voting interface with real-time updates

### For Admins
- **Contest Creation**: Create daily contests with multiple candidates
- **Candidate Management**: Add photos as candidates for contests
- **Winner Selection**: Choose the winning photo from contest candidates
- **Voting Control**: Set voting end times for contests
- **Automatic Candidate System**: Photos with enough likes automatically become candidates
- **Likes Threshold Configuration**: Adjust the minimum likes required for auto-candidates
- **Contest Management**: View, edit, or delete contests
- **Vote Statistics**: View voting statistics and engagement metrics
- **Easy Management**: Simple admin interface for managing all contest content

## 🚀 Getting Started

### 1. Run the Migration
The Photo of the Day Contest tables are automatically created during the main migration process. The system includes:
- `photo_of_day_contest` table for daily contests
- `photo_of_day_candidate` table for contest candidates
- `photo_of_day_vote` table for voting records

### 2. Access the Feature
- **For Guests**: Navigate to "📸 Photo of the Day Contest" in the main navigation
- **For Admins**: Access via the admin panel at `/admin/photo-of-day?key=wedding2024`

## 📱 User Experience

### Guest Voting Flow
1. **Visit Contest Page**: Click "📸 Photo of the Day Contest" in the navigation
2. **View Today's Contest**: See all candidates competing for today's title
3. **Check Voting Status**: See if voting is open or closed
4. **Vote**: Click "Vote" button on your favorite photo (one vote per contest)
5. **See Results**: View real-time vote counts for all candidates
6. **Change Vote**: Click "Remove Vote" to change your mind
7. **View Winners**: See past contest winners in the recent section

### Admin Management Flow
1. **Access Admin Panel**: Go to `/admin/photo-of-day?key=wedding2024`
2. **Create Contest**: Click "Create Today's Contest" to start a new contest
3. **Add Candidates**: Add photos as candidates manually or use auto-candidates
4. **Configure Auto-Candidates**: Set the likes threshold for automatic candidate selection
5. **Monitor Voting**: Watch real-time voting progress
6. **Select Winner**: Choose the winning photo when voting closes
7. **Manage Contests**: View, edit, or delete existing contests

## 🛠️ Technical Details

### Database Schema

#### PhotoOfDayContest Table
```sql
CREATE TABLE photo_of_day_contest (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    contest_date DATE UNIQUE NOT NULL,
    is_active BOOLEAN DEFAULT TRUE,
    voting_ends_at DATETIME,
    winner_photo_id INTEGER,
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (winner_photo_id) REFERENCES photo (id)
);
```

#### PhotoOfDayCandidate Table
```sql
CREATE TABLE photo_of_day_candidate (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    photo_id INTEGER NOT NULL,
    contest_id INTEGER NOT NULL,
    date_added DATE NOT NULL,
    is_winner BOOLEAN DEFAULT FALSE,
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (photo_id) REFERENCES photo (id),
    FOREIGN KEY (contest_id) REFERENCES photo_of_day_contest (id)
);
```

#### PhotoOfDayVote Table
```sql
CREATE TABLE photo_of_day_vote (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    contest_id INTEGER NOT NULL,
    candidate_id INTEGER NOT NULL,
    user_identifier VARCHAR(100) NOT NULL,
    user_name VARCHAR(100) DEFAULT 'Anonymous',
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (contest_id) REFERENCES photo_of_day_contest (id),
    FOREIGN KEY (candidate_id) REFERENCES photo_of_day_candidate (id),
    UNIQUE(contest_id, user_identifier)
);
```

#### Settings Table (for threshold configuration)
```sql
-- The likes threshold is stored in the existing settings table
-- Key: 'photo_of_day_likes_threshold'
-- Default value: '3'
```

### API Endpoints

#### Guest Endpoints
- `GET /photo-of-day` - View today's contest and recent winners
- `POST /api/photo-of-day/vote` - Vote for a candidate in today's contest
- `POST /api/photo-of-day/unvote` - Remove your vote
- `GET /api/photo-of-day/stats` - Get contest statistics

#### Admin Endpoints
- `GET /admin/photo-of-day` - Admin management interface
- `POST /admin/photo-of-day/create-contest` - Create a new contest
- `POST /admin/photo-of-day/select-winner` - Select a winner for a contest
- `POST /admin/photo-of-day/delete-contest/{id}` - Delete a contest
- `POST /admin/photo-of-day/add-candidate` - Add a photo as a candidate
- `POST /admin/photo-of-day/update-threshold` - Update likes threshold for auto-candidates
- `POST /admin/photo-of-day/add-auto-candidates` - Manually trigger adding auto-candidates

## 🎨 Customization

### Styling
The Photo of the Day Contest feature uses the same design system as the rest of the application:
- **Colors**: Pink theme (`#e91e63`) for voting buttons, green (`#4caf50`) for winners
- **Typography**: Inter font family for consistency
- **Layout**: Responsive grid system for mobile and desktop
- **Animations**: Smooth transitions for vote interactions
- **Status Indicators**: Color-coded voting status (open/closed)

### Templates
- `templates/photo_of_day.html` - Main guest interface
- `templates/admin_photo_of_day.html` - Admin management interface

## 🔧 Configuration

### Admin Access
The admin interface is protected by the same key system as other admin features:
- Default key: `wedding2024`
- Access URL: `/admin/photo-of-day?key=wedding2024`

### Contest Configuration
- **Voting Duration**: Optional voting end times for contests
- **Candidate Limits**: No limit on number of candidates per contest
- **Winner Selection**: Manual winner selection by admins
- **Auto-Candidates**: Photos with threshold likes automatically added

### Automatic Candidate Configuration
- **Default Threshold**: 3 likes minimum for auto-candidates
- **Configurable Range**: 1-50 likes threshold
- **Real-time Updates**: Threshold changes apply immediately
- **Visual Indicators**: Winners marked with green badges

### Database Configuration
The feature works with the existing database configuration:
- **SQLite**: Default local development
- **PostgreSQL**: Production deployments
- **Docker**: Containerized deployments

## 📊 Analytics

### Available Statistics
- **Total Votes**: Number of votes cast in each contest
- **Unique Voters**: Number of different users who voted
- **Candidate Performance**: Vote counts for each candidate
- **Contest Engagement**: Overall participation in contests
- **Winner Analytics**: Which types of photos win most often

### Admin Dashboard Metrics
- Total contests created
- Number of candidates across all contests
- Number of auto-candidate eligible photos
- Current likes threshold setting
- Voting engagement statistics
- Recent contest activity overview

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
- **"Already voted"**: Users can only vote once per contest
- **"No contest found"**: Admin needs to create a contest for today
- **"Voting closed"**: Contest voting period has ended

#### Admin Access Issues
- **"Unauthorized"**: Check admin key in URL parameter
- **"Photo not found"**: Ensure photo exists in database
- **"Contest already exists"**: Only one contest per date allowed

#### Contest Management Issues
- **"No candidates found"**: Add photos as candidates first
- **"Winner already selected"**: Only one winner per contest
- **"Invalid candidate"**: Ensure candidate belongs to the contest

### Debug Steps
1. **Check Database**: Verify tables exist with `sqlite3 instance/wedding_photos.db`
2. **Check Settings**: Verify threshold setting: `SELECT * FROM settings WHERE key='photo_of_day_likes_threshold'`
3. **Check Logs**: Review application logs for errors
4. **Test Migration**: Run `python migration.py` to ensure all tables exist
5. **Verify Routes**: Check that blueprints are registered correctly

## 🔮 Future Enhancements

### Planned Features
- **Automatic Winner Selection**: AI-powered winner selection based on votes
- **Voting Campaigns**: Special voting events for specific dates
- **Photo Categories**: Different types of photos (couple, family, friends)
- **Social Sharing**: Share contest winners on social media
- **Email Notifications**: Notify users when new contests start
- **Voting Rewards**: Special badges or recognition for active voters
- **Smart Thresholds**: Dynamic threshold adjustment based on photo volume
- **Batch Auto-Candidate Processing**: Scheduled automatic candidate addition
- **Contest Themes**: Special themed contests (black & white, candid, etc.)

### Integration Ideas
- **Wedding Timeline**: Integrate with wedding event timeline
- **Guest Engagement**: Track guest participation metrics
- **Photo Stories**: Create narratives around contest winners
- **Memory Book**: Compile contest winners into a keepsake book
- **Popularity Analytics**: Track which types of photos win most often

## 📚 Related Documentation

- **[Features Overview](features.md)** - Complete feature breakdown
- **[Installation Guide](installation.md)** - Setup and deployment
- **[Admin Guide](admin.md)** - Admin panel documentation
- **[API Reference](api.md)** - Technical API documentation

---

**Made with ❤️ for your special day**

*Part of the VowVault Wedding Photo Gallery System* 