# SSO (Single Sign-On) Setup Guide

The Wedding Gallery now supports SSO authentication for admin access, allowing you to use your organization's identity provider (Google, Microsoft Azure, Okta, or custom OAuth) instead of just the admin key. **SSO is disabled by default for security.**

## Features

- **Multiple SSO Providers**: Support for Google, Microsoft Azure, Okta, and custom OAuth 2.0
- **Enhanced Security**: CSRF protection with state parameters, timeout handling, and secure session management
- **Flexible Access Control**: Allow specific email addresses or entire domains
- **Fallback Authentication**: Option to keep admin key as backup
- **Session Management**: Secure session handling with automatic logout
- **Admin Panel Integration**: Full integration with existing admin interface
- **Disabled by Default**: SSO is disabled by default for security - must be explicitly enabled

## Security Features

- **CSRF Protection**: State parameter prevents cross-site request forgery attacks
- **Timeout Handling**: Network timeouts prevent hanging requests
- **Secure Session Management**: Proper session cleanup on logout
- **Email Validation**: Ensures valid email addresses from SSO providers
- **Domain Verification**: Supports both individual emails and entire domains
- **Admin Key Fallback**: Optional backup authentication method

## Setup Instructions

### 1. Enable SSO in Admin Panel

1. Go to your admin panel: `/admin?key=wedding2024`
2. Navigate to the "SSO Settings" section
3. Check "Enable SSO Authentication" (disabled by default)
4. Select your SSO provider (Google, Azure, Okta, or Custom)

### 2. Configure OAuth Application

#### For Google:
1. Go to [Google Cloud Console](https://console.developers.google.com/)
2. Create a new project or select existing one
3. Enable Google+ API
4. Go to "Credentials" → "Create Credentials" → "OAuth 2.0 Client IDs"
5. Set Application Type to "Web application"
6. Add authorized redirect URIs: `https://yourdomain.com/sso/callback`
7. Copy the Client ID and Client Secret

**Google OAuth URLs (pre-configured):**
- Authorization URL: `https://accounts.google.com/oauth/authorize`
- Token URL: `https://oauth2.googleapis.com/token`
- User Info URL: `https://www.googleapis.com/oauth2/v2/userinfo`

#### For Microsoft Azure:
1. Go to [Azure Portal](https://portal.azure.com/)
2. Navigate to "Azure Active Directory" → "App registrations"
3. Click "New registration"
4. Set redirect URI to: `https://yourdomain.com/sso/callback`
5. Copy the Application (client) ID and create a client secret
6. Set the authorization URL to your tenant domain

**Azure AD URLs:**
- Authorization URL: `https://login.microsoftonline.com/{tenant-id}/oauth2/v2.0/authorize`
- Token URL: `https://login.microsoftonline.com/{tenant-id}/oauth2/v2.0/token`
- User Info URL: `https://graph.microsoft.com/oidc/userinfo`

#### For Okta:
1. Go to your Okta Admin Console
2. Navigate to "Applications" → "Add Application"
3. Choose "Web Application"
4. Set redirect URI to: `https://yourdomain.com/sso/callback`
5. Copy the Client ID and Client Secret

**Okta URLs:**
- Authorization URL: `https://{your-domain}.okta.com/oauth2/v1/authorize`
- Token URL: `https://{your-domain}.okta.com/oauth2/v1/token`
- User Info URL: `https://{your-domain}.okta.com/oauth2/v1/userinfo`

#### For Custom OAuth:
1. Configure your OAuth server
2. Set the authorization URL, token URL, and user info URL
3. Ensure your OAuth provider supports the required scopes

### 3. Configure Access Control

#### Authorized Email Addresses
Add specific email addresses that are allowed to access the admin panel:
```
admin@company.com
manager@company.com
wedding@company.com
```

#### Authorized Domains
Allow entire domains to access the admin panel:
```
company.com
partner-company.com
```

### 4. Security Settings

#### Admin Key Fallback
- **Enabled (Recommended)**: Admin key can still be used as backup authentication
- **Disabled**: Only SSO authentication is allowed

#### OAuth Scope
Default scope: `openid email profile`
- `openid`: Required for OpenID Connect
- `email`: Required to get user email address
- `profile`: Required to get user name

### 5. Test Configuration

1. Click "Test Connection" for your selected provider
2. Verify the configuration is valid
3. Test the actual SSO login flow

## Security Best Practices

### 1. Keep SSO Disabled by Default
- SSO is disabled by default for security
- Only enable after proper configuration and testing

### 2. Secure Client Secrets
- Never expose client secrets in client-side code
- Store secrets securely in the database
- Rotate secrets regularly

### 3. Use HTTPS
- Always use HTTPS in production
- Configure your domain with SSL certificates

### 4. Monitor Access
- Review admin access logs regularly
- Monitor for suspicious login attempts
- Keep authorized email/domain lists updated

### 5. Backup Authentication
- Keep admin key fallback enabled during initial setup
- Test SSO thoroughly before disabling fallback
- Have a backup admin access method

## Troubleshooting

### Common Issues

#### "SSO not enabled" Error
- Check that SSO is enabled in admin settings
- Verify all required settings are configured

#### "Invalid state parameter" Error
- This is a security feature preventing CSRF attacks
- Try logging in again
- Clear browser cookies if issue persists

#### "Access denied" Error
- Verify your email is in the authorized list
- Check if your domain is in the authorized domains
- Ensure SSO provider is returning correct email address

#### Network Timeout Errors
- Check your internet connection
- Verify SSO provider URLs are correct
- Contact your SSO provider if issues persist

### Testing SSO Configuration

1. **Test Connection**: Use the "Test Connection" button in admin panel
2. **Test Login Flow**: Try the actual SSO login process
3. **Check Logs**: Review application logs for detailed error messages
4. **Verify Settings**: Double-check all configuration values

## Migration from Previous Versions

If you're upgrading from a previous version:

1. **Database Migration**: Run the migration script to add SSO settings
2. **Default Settings**: SSO will be disabled by default
3. **Reconfigure**: Set up your SSO provider again
4. **Test**: Verify everything works before enabling

## API Endpoints

### SSO Routes
- `GET /sso/login` - SSO login page
- `GET /sso/callback` - SSO callback handler
- `GET /sso/logout` - SSO logout
- `GET /auth/test` - Test SSO configuration

### Admin Routes
- `GET /admin/sso-settings` - SSO settings page
- `POST /admin/save-settings` - Save SSO settings

## Security Considerations

### CSRF Protection
- State parameter prevents cross-site request forgery
- Each login attempt generates a unique state value
- State is validated on callback

### Session Security
- SSO sessions are separate from regular user sessions
- Proper session cleanup on logout
- Secure session storage

### Access Control
- Email-based access control
- Domain-based access control
- Fallback to admin key authentication

### Network Security
- HTTPS required for production
- Timeout handling prevents hanging requests
- Secure token exchange

## Support

For SSO-related issues:

1. **Check Configuration**: Verify all settings are correct
2. **Test Connection**: Use the built-in test feature
3. **Review Logs**: Check application logs for errors
4. **Provider Documentation**: Consult your SSO provider's documentation
5. **Security Best Practices**: Follow the security guidelines above

## Changelog

### Version 2.0
- Enhanced security with CSRF protection
- Improved provider support (Google, Azure, Okta, Custom)
- Better error handling and timeout management
- Disabled by default for security
- Enhanced admin interface with provider-specific configuration
- Added comprehensive documentation

### Version 1.0
- Basic SSO implementation
- Google OAuth support
- Simple admin interface 