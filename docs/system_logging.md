# System Logging & Monitoring

The Wedding Gallery application includes a comprehensive system logging and monitoring feature that tracks all system events, errors, and user activities. This helps administrators monitor the application's health, troubleshoot issues, and track user engagement.

## Overview

The system logging feature provides:

- **Real-time monitoring** of application events
- **Error tracking** with detailed stack traces
- **Security event logging** for threat detection
- **Performance monitoring** for upload and processing times
- **User activity tracking** for analytics
- **Admin dashboard** for viewing and managing logs

## Log Types

### System Logs
Track general application events and errors:
- Application startup/shutdown
- Database operations
- File system operations
- Configuration changes
- System errors and exceptions

### Email Processing Logs
Monitor email-based upload functionality:
- Email reception and processing
- Photo extraction from emails
- Success/failure status
- Error messages and responses
- Processing times

### Immich Sync Logs
Track synchronization with Immich server:
- File upload attempts
- Success/failure status
- Asset ID tracking
- Retry attempts
- Error messages

### Upload Logs
Monitor file upload activities:
- Upload attempts and completions
- File validation results
- Processing times
- Error conditions
- User information

### Security Logs
Track security-related events:
- Authentication attempts
- Access violations
- Rate limiting events
- Suspicious activities
- IP address tracking

## Log Levels

The system uses four log levels to categorize events:

- **Info**: Normal application events and successful operations
- **Warning**: Potential issues that don't prevent operation
- **Error**: Problems that affect functionality but are recoverable
- **Critical**: Severe issues that may require immediate attention

## Admin Dashboard

### Accessing Logs
1. Navigate to the Admin Dashboard
2. Click on "System Logs" in the navigation menu
3. View logs organized by type (Email, Immich Sync, System)

### Filtering Logs
Each log section includes filtering options:
- **Email Logs**: All, Success, Errors, Rejected
- **Immich Logs**: All, Success, Errors, Pending
- **System Logs**: All, Info, Warning, Error, Critical, Unresolved

### Log Details
Each log entry shows:
- **Timestamp**: When the event occurred
- **Level**: Info, Warning, Error, or Critical
- **Category**: System, Security, Email, Immich, Upload, Database
- **Message**: Description of the event
- **User**: Who triggered the event (if applicable)
- **IP Address**: Source IP address
- **Status**: Resolved or Open
- **Details**: Additional information (hover to view)

## Log Management

### Automatic Cleanup
- Logs are automatically managed to prevent database bloat
- Older logs are archived or cleaned up based on configuration
- Critical logs are preserved longer than routine events

### Resolution Tracking
- Mark logs as resolved when issues are fixed
- Track who resolved each issue
- Maintain audit trail of problem resolution

### Export and Analysis
- Export logs for external analysis
- Generate reports on system health
- Track trends in errors and performance

## Configuration

### Log Retention
Configure how long to keep different types of logs:
- System logs: 30 days (default)
- Error logs: 90 days (default)
- Security logs: 1 year (default)
- Email/Immich logs: 60 days (default)

### Log Levels
Adjust which events are logged:
- Production: Info, Warning, Error, Critical
- Development: All levels including debug
- Custom: Configure specific categories

## Integration

### Email Notifications
- Receive email alerts for critical errors
- Daily summary of system health
- Immediate notifications for security events

### External Monitoring
- Integrate with external monitoring systems
- Send logs to centralized logging services
- API endpoints for log retrieval

## Best Practices

### Regular Monitoring
- Check logs daily for new errors
- Review security events weekly
- Monitor performance trends monthly

### Error Resolution
- Investigate errors promptly
- Mark resolved issues appropriately
- Document solutions for future reference

### Performance Optimization
- Monitor upload processing times
- Track database query performance
- Identify bottlenecks and optimize

## Troubleshooting

### Common Issues
- **High error rates**: Check system resources and configuration
- **Upload failures**: Verify file permissions and storage space
- **Email processing issues**: Check email server configuration
- **Sync problems**: Verify Immich server connectivity

### Debug Information
- Enable debug logging for detailed troubleshooting
- Export logs for external analysis
- Use admin dashboard filters to isolate specific issues

## Security Considerations

### Data Privacy
- Logs may contain sensitive information
- Implement appropriate access controls
- Consider data retention policies
- Anonymize user data where appropriate

### Access Control
- Restrict log access to authorized administrators
- Audit log access and modifications
- Implement secure log storage

### Compliance
- Ensure logging meets regulatory requirements
- Implement appropriate data retention
- Provide audit trails for compliance 