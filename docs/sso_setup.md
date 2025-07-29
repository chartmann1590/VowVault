# SSO (Single Sign-On) Setup Guide

The Wedding Gallery now supports SSO authentication for admin access, allowing you to use your organization's identity provider (Google, Microsoft Azure, Okta, or custom OAuth) instead of just the admin key.

## Features

- **Multiple SSO Providers**: Support for Google, Microsoft Azure, Okta, and custom OAuth 2.0
- **Flexible Access Control**: Allow specific email addresses or entire domains
- **Fallback Authentication**: Option to keep admin key as backup
- **Session Management**: Secure session handling with automatic logout
- **Admin Panel Integration**: Full integration with existing admin interface

## Setup Instructions

### 1. Enable SSO in Admin Panel

1. Go to your admin panel: `/admin?key=wedding2024`
2. Navigate to the "SSO Security Settings" section
3. Check "Enable SSO Authentication"
4. Select your SSO provider (Google, Azure, Okta, or Custom)

### 2. Configure OAuth Application

#### For Google:
1. Go to [Google Cloud Console](https://console.cloud.google.com/)
2. Create a new project or select existing one
3. Enable Google+ API
4. Go to "Credentials" → "Create Credentials" → "OAuth 2.0 Client IDs"
5. Set Application Type to "Web application"
6. Add authorized redirect URIs: `https://yourdomain.com/sso/callback`
7. Copy the Client ID and Client Secret

#### For Microsoft Azure:
1. Go to [Azure Portal](https://portal.azure.com/)
2. Navigate to "Azure Active Directory" → "App registrations"
3. Click "New registration"
4. Set redirect URI to: `https://yourdomain.com/sso/callback`
5. Copy the Application (client) ID and create a client secret
6. Set the authorization URL to your tenant domain

#### For Okta:
1. Go to your Okta Admin Console
2. Navigate to "Applications" → "Add Application"
3. Choose "Web Application"
4. Set redirect URI to: `https://yourdomain.com/sso/callback`
5. Copy the Client ID and Client Secret

#### For Custom OAuth:
1. Configure your OAuth server
2. Set the authorization URL, token URL, and user info URL
3. Ensure your server supports the required OAuth 2.0 flows

### 3. Configure Admin Panel Settings

In the SSO Security Settings section:

1. **Client ID**: Enter your OAuth client ID
2. **Client Secret**: Enter your OAuth client secret
3. **Redirect URI**: Set to `https://yourdomain.com/sso/callback`
4. **OAuth Scope**: Usually `openid email profile`

For custom providers, also set:
- **Authorization URL**: Your OAuth authorization endpoint
- **Token URL**: Your OAuth token endpoint
- **User Info URL**: Your OAuth userinfo endpoint

### 4. Configure Access Control

#### Allowed Domains:
Enter comma-separated domains (e.g., `example.com, company.com`). Users with emails from these domains will be granted admin access.

#### Allowed Emails:
Enter comma-separated email addresses (e.g., `admin@example.com, user@company.com`). These specific users will be granted admin access.

### 5. Test the Setup

1. Save your SSO settings
2. Click "Test SSO Login" to verify the configuration
3. Try signing in with an authorized account
4. Verify you can access the admin panel

## Security Considerations

### Best Practices:
- **Use HTTPS**: Always use HTTPS in production
- **Strong Client Secrets**: Use strong, unique client secrets
- **Limited Scope**: Request only necessary OAuth scopes
- **Regular Review**: Periodically review authorized users
- **Fallback Key**: Keep admin key as fallback initially

### Access Control:
- **Domain Restrictions**: Limit to your organization's domain
- **Email Whitelist**: Use specific email addresses for fine control
- **Regular Audits**: Review access logs regularly

## Troubleshooting

### Common Issues:

1. **"Invalid redirect URI"**
   - Ensure the redirect URI in your OAuth provider matches exactly
   - Check for trailing slashes or protocol mismatches

2. **"Access denied"**
   - Verify the user's email is in the allowed list
   - Check domain restrictions
   - Ensure the OAuth provider is returning the correct email

3. **"OAuth provider error"**
   - Verify client ID and secret are correct
   - Check that the OAuth app is properly configured
   - Ensure required scopes are requested

4. **"Session expired"**
   - This is normal security behavior
   - Users will need to re-authenticate

### Debug Steps:

1. Check the browser console for JavaScript errors
2. Verify OAuth provider logs
3. Check application logs for SSO-related errors
4. Test with a simple OAuth flow first

## Migration from Key-Based Auth

### Gradual Migration:
1. Enable SSO with admin key fallback
2. Test with a small group of users
3. Gradually add more authorized users
4. Once confident, disable admin key fallback

### Rollback Plan:
- Keep admin key fallback enabled initially
- Monitor SSO usage and errors
- Have admin key ready for emergency access

## Advanced Configuration

### Custom OAuth Providers:
For custom OAuth providers, ensure they support:
- Authorization Code flow
- User info endpoint returning email
- Proper error handling

### Session Configuration:
The system uses Flask sessions for SSO state management. Sessions are secure and encrypted.

### Logging:
SSO authentication attempts are logged for security monitoring.

## Support

For issues with SSO setup:
1. Check the troubleshooting section above
2. Verify your OAuth provider configuration
3. Test with a simple OAuth flow first
4. Review application logs for detailed error messages

## Security Notes

- SSO sessions are secure and encrypted
- User information is not stored permanently
- Access is verified on each admin request
- Automatic logout on session expiration
- No sensitive data is logged 