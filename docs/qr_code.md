# QR Code Feature

The Wedding Gallery includes a comprehensive QR code generation feature that allows administrators to create QR codes for easy sharing of the wedding gallery.

## 🎯 Overview

The QR code feature enables guests to quickly access the wedding gallery by scanning a QR code with their phone camera. This eliminates the need for guests to type in long URLs or remember website addresses.

## 🔧 Admin Configuration

### Accessing QR Settings

1. Navigate to the Admin Dashboard
2. Click on "QR Code Settings" in the admin menu
3. Configure the following options:

### Available Settings

- **Enable/Disable**: Toggle QR code functionality on/off
- **Size Options**: 
  - Small (200px)
  - Medium (300px) 
  - Large (400px)
- **Color Options**:
  - Black
  - Dark Blue
  - Dark Green
  - Dark Red
  - Purple
  - Brown
- **Custom Text**: Optional text to display below the QR code

### QR Code Preview

The admin interface provides a live preview of the QR code with the current settings applied. The preview updates automatically when settings are changed.

## 📱 QR Code Generation

### Preview Endpoint

- **URL**: `/admin/qr-preview`
- **Parameters**:
  - `key`: Admin access key
  - `color`: QR code color (optional, defaults to black)
- **Returns**: PNG image of the QR code

### Download Endpoint

- **URL**: `/admin/download-qr`
- **Parameters**:
  - `key`: Admin access key
  - `format`: Download format (`png` or `svg`)
  - `color`: QR code color (optional)
  - `size`: QR code size (optional)
- **Returns**: Downloadable file in the specified format

### PDF Invitation Generator

- **URL**: `/admin/generate-qr-pdf`
- **Parameters**:
  - `key`: Admin access key
- **Returns**: Beautiful PDF invitation with QR code and all site features

The PDF invitation includes:
- Decorative header and footer
- QR code for easy access
- Email upload instructions with email address
- Complete list of site features
- Usage instructions
- Professional wedding-themed design

## 🎨 Technical Implementation

### QR Code Generation

The QR code is generated using the `qrcode[pil]` library with the following configuration:

```python
qr = qrcode.QRCode(
    version=1,
    error_correction=qrcode.constants.ERROR_CORRECT_L,
    box_size=10,
    border=4,
)
```

### QR Code Data

The QR code contains a URL that points to the wedding gallery with the admin key:

```
{base_url}/?key={admin_key}
```

### Color Support

The QR code supports multiple colors through the PIL library's color parameter:

- Black: `#000000`
- Dark Blue: `#1e3a8a`
- Dark Green: `#166534`
- Dark Red: `#991b1b`
- Purple: `#7c3aed`
- Brown: `#92400e`

## 📊 Usage Statistics

The QR code feature includes:

- **Live Preview**: Real-time preview of QR code with current settings
- **Multiple Formats**: Download as PNG or SVG
- **Size Options**: Three different sizes for various use cases
- **Color Customization**: Six different color options
- **Custom Text**: Optional text display below the QR code
- **PDF Invitation**: Generate beautiful invitation-style PDFs with QR code and all features

## 🖨️ Printing and Display

### Recommended Uses

1. **PDF Invitations**: Generate beautiful invitation PDFs with QR codes
2. **Wedding Invitations**: Print QR codes on invitations
3. **Table Cards**: Add QR codes to table cards
4. **Venue Display**: Display QR codes at the wedding venue
5. **Wedding Programs**: Include QR codes in programs
6. **Thank You Cards**: Add QR codes to thank you cards

### Digital Sharing

1. **Social Media**: Share QR codes on social media platforms
2. **Email/Text**: Send QR codes via email or text message
3. **Wedding Website**: Include QR codes on wedding websites
4. **Digital Invitations**: Add QR codes to digital invitations

## 🔒 Security Considerations

- QR codes require the admin key for access
- Admin authentication is required for QR code generation
- QR codes are generated on-demand for security
- No QR codes are stored permanently in the database

## 🛠️ Troubleshooting

### Common Issues

1. **QR Code Not Loading**: Check admin authentication and key validity
2. **Wrong Colors**: Ensure the color parameter is correctly passed
3. **Download Issues**: Verify the format parameter is correct (`png` or `svg`)

### Error Handling

The QR code endpoints include proper error handling:

- Unauthorized access returns 401 status
- Invalid parameters are handled gracefully
- Missing dependencies are caught and reported

## 📈 Future Enhancements

Potential improvements for the QR code feature:

- **Custom Logo Integration**: Add custom logos to QR codes
- **Analytics Tracking**: Track QR code scans and usage
- **Multiple QR Codes**: Generate different QR codes for different purposes
- **QR Code Templates**: Pre-designed templates for different use cases
- **Batch Generation**: Generate multiple QR codes at once

## 🔗 Related Documentation

- [Admin Dashboard Guide](ADMIN_DASHBOARD.md)
- [Admin Organization](ADMIN_ORGANIZATION.md)
- [Features Overview](features.md) 