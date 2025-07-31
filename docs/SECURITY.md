# 🔒 Security Guide

This document outlines the comprehensive security measures implemented in the Wedding Gallery application to protect user privacy and data integrity.

## 🛡️ Security Features

### Database Security

#### SQLite Database Protection
- **WAL Mode**: Enabled for better concurrency and data integrity
- **Foreign Key Constraints**: Enforced for data consistency
- **Secure Pragma Settings**: Optimized for security and performance
- **File Permissions**: Database files set to 640 (owner read/write, group read, others none)

#### Database Encryption
- Database files are stored with restricted permissions
- Audit logging for all database operations
- Integrity checks using SHA-256 hashes

### File Upload Security

#### File Validation
- **Extension Validation**: Only allowed image and video extensions
- **Content Validation**: Magic byte detection for file type verification
- **Size Limits**: Configurable maximum file size (default: 50MB)
- **MIME Type Detection**: Server-side MIME type validation
- **Dangerous File Blocking**: Automatic blocking of executable and script files

#### Secure File Storage
- **Filename Sanitization**: All filenames are sanitized using `secure_filename`
- **Unique Filenames**: Automatic collision resolution
- **File Integrity**: SHA-256 hash calculation for integrity verification
- **Secure Permissions**: Upload directories set to 755

#### Blocked File Types
The following file types are automatically blocked:
```
Executables: .exe, .bat, .cmd, .com, .pif, .scr
Scripts: .vbs, .js, .jar, .war
Web Files: .php, .asp, .aspx, .jsp, .py, .pl, .sh, .cgi
Config Files: .htaccess, .htpasswd, .ini, .log, .tmp, .temp, .bak, .backup
```

### Rate Limiting

#### Application-Level Rate Limiting
- **Upload Rate Limit**: 5 uploads per 5 minutes per client
- **API Rate Limit**: 10 requests per minute per client
- **Login Rate Limit**: 3 attempts per minute per client
- **Guestbook Rate Limit**: 3 entries per 5 minutes per client
- **Message Rate Limit**: 3 messages per 5 minutes per client

#### Nginx-Level Rate Limiting
- **Upload Endpoint**: 5 requests per minute with burst of 3
- **API Endpoints**: 10 requests per minute with burst of 5
- **Admin Access**: 3 requests per minute with burst of 2

### Security Headers

The application includes comprehensive security headers:

```nginx
X-Frame-Options: SAMEORIGIN
X-Content-Type-Options: nosniff
X-XSS-Protection: 1; mode=block
Referrer-Policy: strict-origin-when-cross-origin
Content-Security-Policy: default-src 'self'; script-src 'self' 'unsafe-inline' 'unsafe-eval'; style-src 'self' 'unsafe-inline'; img-src 'self' data: blob:; font-src 'self'; connect-src 'self'; frame-ancestors 'self';
Permissions-Policy: geolocation=(), microphone=(), camera=()
Strict-Transport-Security: max-age=31536000; includeSubDomains
```

### Audit Logging

#### Security Event Logging
All security-relevant events are logged to the database:

- **Upload Attempts**: All file upload attempts with client information
- **Rate Limit Violations**: When users exceed rate limits
- **Invalid File Attempts**: Attempts to upload blocked file types
- **Admin Access**: All admin panel access attempts
- **Authentication Events**: Login attempts and failures
- **File Integrity Checks**: File hash verification results

#### Log Retention
- **Default Retention**: 30 days
- **Configurable**: Via `SECURITY_LOG_RETENTION_DAYS` environment variable
- **Automatic Cleanup**: Old logs are automatically removed

### Input Validation and Sanitization

#### User Input Sanitization
- **Filename Sanitization**: Using Werkzeug's `secure_filename`
- **HTML Escaping**: All user-generated content is properly escaped
- **SQL Injection Prevention**: Using parameterized queries
- **XSS Prevention**: Content Security Policy and input validation

#### File Content Validation
- **Magic Byte Detection**: Validates file content against expected signatures
- **MIME Type Verification**: Server-side MIME type checking
- **Size Validation**: Prevents oversized file uploads
- **Extension Validation**: Double-checks file extensions

## 🔧 Security Configuration

### Environment Variables

```bash
# Security Configuration
SECRET_KEY=your-secure-secret-key-here
ADMIN_KEY=your-secure-admin-key
ADMIN_EMAIL=admin@your-domain.com

# Rate Limiting
RATE_LIMIT_UPLOAD_MAX=5
RATE_LIMIT_UPLOAD_WINDOW=5
RATE_LIMIT_API_MAX=10
RATE_LIMIT_API_WINDOW=1
RATE_LIMIT_LOGIN_MAX=3
RATE_LIMIT_LOGIN_WINDOW=1

# File Upload Security
MAX_CONTENT_LENGTH=52428800
ALLOWED_IMAGE_EXTENSIONS=png,jpg,jpeg,gif,webp
ALLOWED_VIDEO_EXTENSIONS=mp4,mov,avi,webm
MAX_VIDEO_DURATION=15

# Security Logging
SECURITY_LOG_RETENTION_DAYS=30
SECURITY_LOG_LEVEL=info
```

### Production Security Checklist

#### Before Deployment
- [ ] Change default `SECRET_KEY` to a strong random value
- [ ] Change default `ADMIN_KEY` to a secure value
- [ ] Set up HTTPS/SSL certificates
- [ ] Configure proper backup strategy
- [ ] Set up monitoring and alerting
- [ ] Review and customize rate limiting settings
- [ ] Configure firewall rules
- [ ] Set up intrusion detection

#### Runtime Security
- [ ] Monitor security audit logs regularly
- [ ] Review rate limit violations
- [ ] Check for suspicious file uploads
- [ ] Verify file integrity periodically
- [ ] Update dependencies regularly
- [ ] Monitor system resources

#### Network Security
- [ ] Use HTTPS in production
- [ ] Configure proper firewall rules
- [ ] Use Cloudflare or similar CDN for additional protection
- [ ] Implement proper DNS security
- [ ] Consider using a VPN for admin access

## 🚨 Security Monitoring

### Security Audit Logs

The application maintains detailed security audit logs in the `security_audit_log` table:

```sql
SELECT event_type, user_identifier, ip_address, details, severity, created_at 
FROM security_audit_log 
ORDER BY created_at DESC 
LIMIT 50;
```

### Common Security Events

#### Normal Events (Info Level)
- `upload_attempt`: Normal file upload attempts
- `file_uploaded`: Successful file uploads
- `admin_access`: Admin panel access

#### Warning Events (Warning Level)
- `rate_limit_exceeded`: Users exceeding rate limits
- `invalid_file_extension`: Attempts to upload blocked files
- `suspicious_activity`: Unusual patterns detected

#### Critical Events (Error Level)
- `invalid_file_content`: Malicious file content detected
- `file_integrity_failed`: File corruption detected
- `security_violation`: Serious security violations

### Monitoring Queries

#### Rate Limit Violations
```sql
SELECT ip_address, COUNT(*) as violations 
FROM security_audit_log 
WHERE event_type = 'rate_limit_exceeded' 
AND created_at > datetime('now', '-1 day')
GROUP BY ip_address 
ORDER BY violations DESC;
```

#### Suspicious File Attempts
```sql
SELECT ip_address, details, created_at 
FROM security_audit_log 
WHERE event_type IN ('invalid_file_extension', 'invalid_file_content')
AND created_at > datetime('now', '-7 days')
ORDER BY created_at DESC;
```

#### Failed Admin Access
```sql
SELECT ip_address, user_agent, created_at 
FROM security_audit_log 
WHERE event_type = 'admin_access_failed'
AND created_at > datetime('now', '-1 day')
ORDER BY created_at DESC;
```

## 🔐 Privacy Protection

### Data Minimization
- **IP Address Logging**: Only for security purposes, not for user tracking
- **User Identifiers**: Anonymous identifiers for rate limiting
- **File Metadata**: Minimal metadata collection
- **No Personal Data**: No unnecessary personal information collection

### Data Retention
- **Security Logs**: 30 days (configurable)
- **Uploaded Files**: Until manually deleted
- **Database Records**: Until manually deleted
- **Rate Limit Data**: Automatically cleaned up

### Access Control
- **Admin Access**: Restricted to authorized users only
- **File Access**: Public read access for uploaded files
- **Database Access**: Restricted to application only
- **Configuration Files**: Restricted permissions

## 🛠️ Security Tools

### Built-in Security Utilities

The application includes a comprehensive `SecurityUtils` class with:

- **File Validation**: Complete file upload security
- **Rate Limiting**: Application-level rate limiting
- **Audit Logging**: Comprehensive security event logging
- **File Integrity**: Hash-based integrity verification
- **Input Sanitization**: Secure input handling

### Security Dependencies

```python
python-magic==0.4.27    # File type detection
cryptography==41.0.7     # Cryptographic functions
```

**Note**: The `python-magic` library requires the `libmagic1` system library, which is included in the Docker container. For local development, you may need to install it separately:

```bash
# Ubuntu/Debian
sudo apt-get install libmagic1

# macOS
brew install libmagic

# CentOS/RHEL
sudo yum install file-devel
```

## 📋 Security Best Practices

### For Administrators
1. **Regular Updates**: Keep the application and dependencies updated
2. **Strong Passwords**: Use strong, unique passwords for admin access
3. **HTTPS Only**: Always use HTTPS in production
4. **Backup Strategy**: Implement regular backups with encryption
5. **Monitoring**: Set up monitoring for security events
6. **Access Control**: Limit admin access to trusted IPs

### For Users
1. **File Uploads**: Only upload appropriate image and video files
2. **Rate Limits**: Respect upload and posting rate limits
3. **Privacy**: Be mindful of personal information in uploads
4. **Reporting**: Report suspicious activity to administrators

### For Developers
1. **Code Review**: Review all security-related code changes
2. **Testing**: Test security features thoroughly
3. **Documentation**: Keep security documentation updated
4. **Dependencies**: Regularly update security dependencies

## 🚨 Incident Response

### Security Incident Response Plan

1. **Detection**: Monitor security audit logs for suspicious activity
2. **Assessment**: Evaluate the severity and scope of the incident
3. **Containment**: Isolate affected systems and prevent further damage
4. **Investigation**: Gather evidence and determine root cause
5. **Remediation**: Fix vulnerabilities and restore systems
6. **Recovery**: Restore normal operations
7. **Post-Incident**: Document lessons learned and improve security

### Emergency Contacts
- **System Administrator**: [Your Contact Information]
- **Security Team**: [Security Contact Information]
- **Hosting Provider**: [Provider Contact Information]

## 📚 Additional Resources

- [OWASP Top 10](https://owasp.org/www-project-top-ten/)
- [Flask Security Best Practices](https://flask-security.readthedocs.io/)
- [Nginx Security Headers](https://nginx.org/en/docs/http/ngx_http_headers_module.html)
- [SQLite Security](https://www.sqlite.org/security.html)

---

**Note**: This security guide should be reviewed and updated regularly to ensure it reflects current security best practices and any changes to the application. 