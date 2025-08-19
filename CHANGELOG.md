# Changelog

All notable changes to VowVault will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [Unreleased]

### Added
- Comprehensive GitHub workflows for CI/CD
- Development requirements and tools
- Pre-commit hooks for code quality
- Development documentation and guides
- Contributing guidelines

### Changed
- Updated README with badges and better organization
- Improved documentation structure
- Enhanced development setup instructions

## [1.0.0] - 2024-01-XX

### Added
- Initial release of VowVault
- Wedding photo gallery with drag & drop upload
- SSO authentication support (Google, Microsoft, Okta)
- Progressive Web App (PWA) features
- Virtual photobooth with custom borders
- Message board and digital guestbook
- QR code generation for easy sharing
- Comprehensive admin dashboard
- Timezone support and management
- Email integration for photo uploads
- Video upload and playback support
- Like and comment system
- Slideshow mode
- Mobile-responsive design

### Security
- CSRF protection
- Secure session management
- Admin key fallback authentication
- Email and domain-based access control
- Enhanced security features

### Technical
- Flask-based web application
- SQLAlchemy database integration
- Docker containerization support
- Nginx reverse proxy configuration
- Comprehensive error handling
- Logging and monitoring capabilities

## [0.9.0] - 2024-01-XX

### Added
- Beta version with core features
- Basic photo upload and gallery
- Simple authentication system
- Admin panel foundation

### Changed
- Initial development and testing
- User feedback integration
- Performance optimizations

## [0.8.0] - 2024-01-XX

### Added
- Alpha version development
- Core application structure
- Database models and migrations
- Basic UI templates

### Changed
- Architecture planning and implementation
- Database schema design
- Frontend framework selection

---

## Release Notes

### Version 1.0.0
This is the first stable release of VowVault, featuring a complete wedding photo gallery solution with advanced features like SSO authentication, PWA support, and comprehensive admin tools.

### Breaking Changes
- None in this release

### Migration Guide
- Fresh installation recommended
- No data migration required

### Known Issues
- Some SSO providers may require additional configuration
- Video processing may be slow on low-end devices

---

## Contributing to Changelog

When adding entries to the changelog, follow these guidelines:

1. **Use the present tense** ("Add feature" not "Added feature")
2. **Use the imperative mood** ("Move cursor to..." not "Moves cursor to...")
3. **Reference issues and pull requests** liberally after the relevant entry
4. **Don't assume knowledge** about what has changed
5. **Describe what users can do** with the new functionality

### Changelog Entry Types

- **Added** for new features
- **Changed** for changes in existing functionality
- **Deprecated** for soon-to-be removed features
- **Removed** for now removed features
- **Fixed** for any bug fixes
- **Security** in case of vulnerabilities

### Example Entry

```markdown
### Added
- New photo filter effects
- Batch photo operations
- Export functionality for albums

### Changed
- Improved upload performance by 40%
- Updated UI design for better mobile experience

### Fixed
- Resolved issue with photo rotation on iOS devices
- Fixed memory leak in slideshow mode
```