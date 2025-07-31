# Timezone Settings

## Overview

The Wedding Gallery application now includes timezone support for the admin interface. This allows administrators to view all dates and times in their local timezone, making it easier to manage the gallery from anywhere in the world.

## Features

### Admin Timezone Configuration
- **Timezone Selection**: Admins can choose from a comprehensive list of timezones including:
  - UTC (Coordinated Universal Time)
  - US Timezones: Eastern, Central, Mountain, Pacific
  - European Timezones: London, Paris, Berlin
  - Asian Timezones: Tokyo, Shanghai
  - Australian Timezones: Sydney, Auckland

### Automatic Date/Time Formatting
- All dates and times in the admin interface are automatically displayed in the selected timezone
- Affected areas include:
  - Photo upload dates
  - Guestbook entry dates
  - Message board post dates
  - Comment timestamps
  - Email log timestamps
  - System log timestamps

### Real-time Preview
- The timezone settings page shows the current time in the selected timezone
- Timezone changes are reflected immediately in the preview

## Configuration

### Setting the Timezone
1. Navigate to the Admin Dashboard
2. Scroll to the "Timezone Settings" section
3. Select your desired timezone from the dropdown menu
4. Click "Save Timezone Settings"
5. The change will be applied immediately

### Default Timezone
- The system defaults to UTC if no timezone is selected
- This ensures consistent behavior across different server locations

## Technical Implementation

### Database Storage
- Timezone settings are stored in the `settings` table
- Key: `timezone_settings`
- Value: JSON object containing timezone information

### Backend Processing
- Uses the `pytz` library for timezone handling
- Includes fallback to UTC if invalid timezone is selected
- Jinja2 template filter `timezone_format` for consistent formatting

### Frontend Integration
- JavaScript updates timezone preview in real-time
- Settings are saved via AJAX to prevent page reloads

## Migration

The timezone feature is automatically initialized during database migration:
- Default timezone settings are created if they don't exist
- No manual migration steps required
- Compatible with existing installations

## Benefits

1. **Global Accessibility**: Admins can work from any timezone
2. **Consistent Experience**: All dates/times are displayed in local time
3. **No Confusion**: Eliminates timezone-related misunderstandings
4. **Professional Management**: Proper timezone handling for international events

## Troubleshooting

### Timezone Not Updating
- Ensure the timezone setting is saved in the admin interface
- Check that the selected timezone is valid
- Refresh the page after saving settings

### Invalid Timezone
- The system will fallback to UTC if an invalid timezone is detected
- Check the timezone selection in the admin settings

### Database Issues
- Run the migration script to ensure timezone settings are initialized
- Check that the `settings` table contains the `timezone_settings` entry

## Future Enhancements

- Automatic timezone detection based on user location
- Per-user timezone preferences
- Timezone-aware scheduling features
- Integration with calendar systems 