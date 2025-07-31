# 📱 Progressive Web App (PWA)

## What is PWA?
VowVault includes full Progressive Web App functionality, allowing guests to install the wedding gallery as a native app on their mobile devices for quick access.

## PWA Features
- **📱 Native App Experience** - Install on home screen like a regular app
- **🔄 Offline Support** - Caches essential resources for offline viewing
- **⚡ Fast Loading** - Optimized for quick access and smooth performance
- **📱 Mobile-First** - Designed specifically for mobile devices
- **🎨 Custom Icons** - Beautiful wedding-themed app icons
- **🔗 App Shortcuts** - Quick access to Upload, Photobooth, and Messages

## Installation Instructions

### For Android/Chrome Users:
1. Open Chrome browser on your Android device
2. Navigate to the wedding gallery website
3. Tap the menu button (⋮) in Chrome
4. Select "Add to Home screen" or "Install app"
5. Follow the prompts to install

### For iPhone/Safari Users:
1. Open Safari browser on your iPhone
2. Navigate to the wedding gallery website
3. Tap the share button (📤) in Safari
4. Scroll down and tap "Add to Home Screen"
5. Tap "Add" to install the app

### For Other Browsers:
1. Look for an install prompt or menu option
2. Select "Install" or "Add to Home Screen"
3. Follow the browser's specific instructions

## PWA Requirements
- **HTTPS Required** - PWA features only work with valid SSL certificates
- **Self-signed certificates** will not work for PWA installation
- **Production deployment** should use proper SSL certificates (Let's Encrypt, etc.)

## Troubleshooting PWA Issues

### Development/Testing:
- Use Chrome DevTools → Application → Manifest → "Add to home screen"
- Check browser console for PWA debug messages
- Visit `/admin/pwa-debug?key=your-key` for detailed analysis

### Production Setup:
- Ensure valid SSL certificate is installed
- Verify manifest.json is accessible at `/static/manifest.json`
- Check service worker registration in browser console
- Test on multiple devices and browsers

## PWA Debug Tools
The admin panel includes comprehensive PWA debugging tools:
- **Requirements Check** - Verify HTTPS, manifest, service worker, and icons
- **Connection Analysis** - View host, URL, and user agent details
- **Troubleshooting Guide** - Solutions for common PWA issues
- **Quick Actions** - Direct links to manifest and service worker files

## Technical Implementation

### Manifest File
The `manifest.json` file defines the PWA properties:
- App name and description
- Theme colors and background
- Icon definitions for different sizes
- Display mode and orientation
- App shortcuts for quick access

### Service Worker
The `sw.js` service worker provides:
- Offline caching of essential resources
- Background sync capabilities
- Cache management and updates
- Network request interception

**Service Worker Route**: The service worker is served at `/sw.js` with proper JavaScript MIME type for optimal browser compatibility.

### Icons
Multiple icon sizes are provided for different devices:
- 16x16, 32x32, 72x72, 96x96, 128x128
- 144x144, 152x152, 192x192, 384x384, 512x512
- Maskable icons for adaptive design

## PWA Benefits

### For Guests
- **Quick Access** - One tap to open the gallery
- **Offline Viewing** - View cached photos without internet
- **Native Feel** - App-like experience without app store
- **Space Efficient** - No large app downloads required

### For Administrators
- **Better Engagement** - Guests more likely to use installed app
- **Reduced Bounce Rate** - Quick access increases usage
- **Professional Appearance** - Native app experience
- **Analytics** - Track PWA installation and usage

## Advanced Configuration

### Customizing the PWA
- **App Name** - Edit in `manifest.json`
- **Theme Colors** - Match your wedding colors
- **Icons** - Replace with custom wedding-themed icons
- **Shortcuts** - Add quick access to specific features

### Performance Optimization
- **Cache Strategy** - Optimize for your use case
- **Icon Optimization** - Use appropriate sizes
- **Loading Speed** - Minimize initial load time
- **Offline Content** - Cache essential resources

## Security Considerations

### HTTPS Requirements
- PWA features require HTTPS
- Self-signed certificates don't work
- Use Let's Encrypt for free SSL
- Configure proper SSL in production

### Content Security Policy
- Ensure CSP allows service worker
- Configure for your domain
- Test PWA functionality with CSP

## Testing PWA

### Development Testing
1. Use Chrome DevTools
2. Check Application tab
3. Test manifest and service worker
4. Verify offline functionality

### Production Testing
1. Test on multiple devices
2. Verify HTTPS setup
3. Check installation prompts
4. Test offline functionality

## Common Issues

### Service Worker 404 Error
If you see `GET /sw.js HTTP/1.1" 404` in logs:
- ✅ **Fixed**: Service worker is now properly served at `/sw.js` via the main blueprint
- The route was added to `app/views/main.py` to handle service worker requests
- Uses correct static folder path (`../static`) for modular structure
- Check browser console for successful registration
- Verify HTTPS setup for production use

### Installation Not Available
- Check HTTPS setup
- Verify manifest.json accessibility
- Test on supported browsers
- Check service worker registration

### Offline Not Working
- Verify service worker installation
- Check cache configuration
- Test network conditions
- Review cache strategies

### Icons Not Displaying
- Verify icon file paths
- Check icon sizes and formats
- Test on different devices
- Validate manifest.json 