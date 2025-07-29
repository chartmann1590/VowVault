# Immich Server Integration

VowVault now supports automatic synchronization with your own Immich server! This allows you to automatically sync all wedding gallery uploads to your personal Immich instance.

## What Gets Synced

When Immich sync is enabled, the following content will be automatically synced to your Immich server:

- **Photos & Videos**: All uploaded photos and videos from the main gallery
- **Guestbook Photos**: Photos attached to guestbook entries
- **Message Photos**: Photos attached to message board posts
- **Photobooth Photos**: Photos from the virtual photobooth feature

## Setup Instructions

### 1. Immich Server Setup

First, ensure you have an Immich server running. You can:
- Self-host Immich using Docker
- Use a hosted Immich instance
- Set up Immich on your own server

### 2. Get Your API Key

1. Log into your Immich server
2. Go to **Admin → Settings → API Keys**
3. Create a new API key
4. Copy the API key (you'll need this for configuration)

### 3. Configure VowVault

#### Option A: Environment Variables

Add these to your `.env` file:

```bash
# Immich Configuration
IMMICH_ENABLED=true
IMMICH_SERVER_URL=https://your-immich-server.com
IMMICH_API_KEY=your-api-key-here
IMMICH_USER_ID=your-user-id
IMMICH_ALBUM_NAME=Wedding Gallery
```

#### Option B: Admin Panel Configuration

1. Go to the admin panel (`/admin?key=wedding2024`)
2. Scroll to the **Immich Server Sync Settings** section
3. Enable **Immich Sync**
4. Enter your server URL (e.g., `https://immich.yourdomain.com`)
5. Enter your API key
6. Optionally enter your user ID
7. Set the album name (default: "Wedding Gallery")
8. Configure which content types to sync
9. Click **Save Immich Settings**

### 4. Test the Connection

1. In the admin panel, click **Sync Now** to test the connection
2. Check the **Immich Sync Log** section for any errors
3. Verify files appear in your Immich server

## Configuration Options

### Sync Settings

You can control what gets synced:

- **Sync Photos**: Regular gallery photos
- **Sync Videos**: Gallery videos
- **Sync Guestbook Photos**: Photos from guestbook entries
- **Sync Message Photos**: Photos from message board
- **Sync Photobooth Photos**: Virtual photobooth photos

### Album Organization

All synced content will be added to the specified album in your Immich server. The album will be created automatically if it doesn't exist.

### File Descriptions

Each synced file includes descriptive metadata:
- **Photos**: "Wedding photo by [uploader name] - [description]"
- **Videos**: "Wedding video by [uploader name] - [description]"
- **Guestbook**: "Guestbook photo by [name] from [location] - [message]"
- **Messages**: "Message photo by [author] - [content]"
- **Photobooth**: "Photobooth photo by [uploader name] - [description]"

## Troubleshooting

### Common Issues

1. **Connection Failed**
   - Verify your server URL is correct
   - Check that your Immich server is accessible
   - Ensure your API key is valid

2. **Files Not Syncing**
   - Check the sync logs in the admin panel
   - Verify the file types are supported by Immich
   - Ensure you have sufficient storage on your Immich server

3. **API Key Issues**
   - Generate a new API key in Immich admin
   - Ensure the API key has proper permissions
   - Check that the user ID matches the API key owner

### Sync Logs

The admin panel includes detailed sync logs showing:
- Which files were synced
- Success/error status
- Immich asset IDs
- Error messages for failed syncs

### Manual Sync

You can manually trigger a sync of all existing content:
1. Go to admin panel
2. Click **Sync Now** in the Immich settings section
3. This will sync all eligible files that haven't been synced yet

## Security Notes

- API keys are stored securely in the database
- Sync operations are logged for audit purposes
- Failed syncs are retried automatically
- No sensitive data is transmitted to Immich

## Performance Considerations

- Sync operations happen in the background
- Large files may take time to upload
- Consider your server's upload bandwidth
- Monitor disk space on your Immich server

## Advanced Configuration

### Custom Album Names

You can organize content into different albums by changing the album name in settings. For example:
- "Wedding Gallery - Photos"
- "Wedding Gallery - Videos"
- "Wedding Gallery - Guestbook"

### Selective Syncing

Disable specific content types if you don't want everything synced:
- Uncheck "Sync Videos" if you only want photos
- Uncheck "Sync Guestbook" if you want only main gallery content
- Uncheck "Sync Photobooth" if you want to keep those separate

## Support

If you encounter issues with the Immich integration:

1. Check the sync logs in the admin panel
2. Verify your Immich server configuration
3. Test the API connection manually
4. Check the application logs for detailed error messages

The Immich integration provides a seamless way to keep your wedding photos organized in your personal photo library while maintaining the social sharing features of VowVault. 