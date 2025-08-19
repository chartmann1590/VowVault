# Contributing to VowVault

Thank you for your interest in contributing to VowVault! This document provides guidelines and information for contributors.

## 🤝 How to Contribute

### Types of Contributions

We welcome various types of contributions:

- **Bug Reports**: Help us identify and fix issues
- **Feature Requests**: Suggest new features or improvements
- **Code Contributions**: Submit pull requests with code changes
- **Documentation**: Improve or add to our documentation
- **Testing**: Help test features and report issues
- **Design**: Suggest UI/UX improvements

### Before You Start

1. **Check existing issues**: Search [GitHub Issues](https://github.com/chartmann1590/VowVault/issues) to see if your idea has already been discussed
2. **Read the documentation**: Familiarize yourself with the project structure and existing features
3. **Join the discussion**: Comment on existing issues or start new discussions

## 🚀 Getting Started

### Prerequisites

- Python 3.8+
- Git
- Docker (optional, for containerized development)

### Development Setup

1. **Fork the repository**
   ```bash
   # Click "Fork" on GitHub, then clone your fork
   git clone https://github.com/your-username/VowVault.git
   cd VowVault
   ```

2. **Set up the development environment**
   ```bash
   # Create virtual environment
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   
   # Install dependencies
   pip install -r requirements.txt
   pip install -r requirements-dev.txt  # Development dependencies
   ```

3. **Set up pre-commit hooks** (optional but recommended)
   ```bash
   pre-commit install
   ```

4. **Run the application**
   ```bash
   python run.py
   ```

5. **Verify setup**
   - Open http://localhost:5000 in your browser
   - Access admin panel at http://localhost:5000/admin?key=wedding2024

## 📝 Development Workflow

### Branch Naming Convention

Use descriptive branch names following this pattern:
- `feature/description` - for new features
- `bugfix/description` - for bug fixes
- `docs/description` - for documentation updates
- `refactor/description` - for code refactoring

Examples:
- `feature/photo-filters`
- `bugfix/upload-error-handling`
- `docs/api-documentation`

### Commit Message Guidelines

Follow the [Conventional Commits](https://www.conventionalcommits.org/) specification:

```
<type>[optional scope]: <description>

[optional body]

[optional footer(s)]
```

Types:
- `feat`: New feature
- `fix`: Bug fix
- `docs`: Documentation changes
- `style`: Code style changes (formatting, etc.)
- `refactor`: Code refactoring
- `test`: Adding or updating tests
- `chore`: Maintenance tasks

Examples:
```
feat: add photo filters and effects
fix(auth): resolve SSO login timeout issue
docs: update installation guide for Docker
style: format code with black
```

### Pull Request Process

1. **Create a feature branch** from `main`
   ```bash
   git checkout main
   git pull origin main
   git checkout -b feature/your-feature-name
   ```

2. **Make your changes** and commit them
   ```bash
   git add .
   git commit -m "feat: add your new feature"
   ```

3. **Push your branch** to your fork
   ```bash
   git push origin feature/your-feature-name
   ```

4. **Create a Pull Request** on GitHub
   - Use the PR template if available
   - Provide a clear description of your changes
   - Link any related issues
   - Include screenshots for UI changes

5. **Code Review Process**
   - Maintainers will review your PR
   - Address any feedback or requested changes
   - Ensure all CI checks pass

## 🧪 Testing

### Running Tests

```bash
# Run all tests
python -m pytest

# Run tests with coverage
python -m pytest --cov=app

# Run specific test file
python -m pytest tests/test_auth.py

# Run tests in parallel
python -m pytest -n auto
```

### Writing Tests

- Write tests for new features
- Ensure existing tests pass
- Aim for good test coverage
- Use descriptive test names
- Test both success and failure cases

### Test Structure

```
tests/
├── unit/           # Unit tests
├── integration/    # Integration tests
├── fixtures/       # Test fixtures
└── conftest.py     # Test configuration
```

## 📚 Documentation

### Documentation Standards

- Use clear, concise language
- Include code examples
- Keep documentation up-to-date with code changes
- Use consistent formatting and structure

### Documentation Structure

```
docs/
├── features.md         # Feature descriptions
├── installation.md     # Setup instructions
├── usage.md           # User guides
├── api.md             # API documentation
└── development.md     # Developer guides
```

## 🔧 Code Quality

### Code Style

We use several tools to maintain code quality:

- **Black**: Code formatting
- **Flake8**: Linting
- **isort**: Import sorting
- **mypy**: Type checking

### Running Code Quality Checks

```bash
# Format code
black app/ tests/

# Sort imports
isort app/ tests/

# Lint code
flake8 app/ tests/

# Type checking
mypy app/
```

### Pre-commit Hooks

Install pre-commit hooks to automatically run quality checks:

```bash
pip install pre-commit
pre-commit install
```

## 🐛 Bug Reports

### Before Reporting

1. Check if the issue has already been reported
2. Try to reproduce the issue
3. Check the documentation for solutions

### Bug Report Template

Use this template when creating bug reports:

```markdown
## Bug Description
Brief description of the issue

## Steps to Reproduce
1. Step 1
2. Step 2
3. Step 3

## Expected Behavior
What you expected to happen

## Actual Behavior
What actually happened

## Environment
- OS: [e.g., Ubuntu 20.04]
- Python Version: [e.g., 3.9.7]
- VowVault Version: [e.g., commit hash or version]

## Additional Information
Any other context, logs, or screenshots
```

## 💡 Feature Requests

### Feature Request Guidelines

- Be specific about what you want
- Explain why the feature would be useful
- Consider implementation complexity
- Provide examples or mockups if possible

### Feature Request Template

```markdown
## Feature Description
Brief description of the requested feature

## Use Case
Why this feature would be useful

## Proposed Implementation
How you think it could be implemented

## Alternatives Considered
Other approaches you've considered

## Additional Information
Any other relevant details
```

## 🚀 Release Process

### Versioning

We use [Semantic Versioning](https://semver.org/):
- `MAJOR.MINOR.PATCH`
- Major: Breaking changes
- Minor: New features (backward compatible)
- Patch: Bug fixes (backward compatible)

### Release Checklist

- [ ] All tests pass
- [ ] Documentation is updated
- [ ] Changelog is updated
- [ ] Version is bumped
- [ ] Release notes are written

## 📞 Getting Help

### Communication Channels

- **GitHub Issues**: For bugs, features, and questions
- **GitHub Discussions**: For general discussion and help
- **Pull Requests**: For code contributions

### Asking for Help

When asking for help:

1. **Be specific** about your problem
2. **Include relevant code** and error messages
3. **Describe what you've tried** already
4. **Provide context** about your environment

## 🏆 Recognition

Contributors are recognized in several ways:

- **Contributors list** on GitHub
- **Changelog entries** for significant contributions
- **Special thanks** in release notes for major contributions

## 📋 Contributor Checklist

Before submitting your contribution, ensure you have:

- [ ] Read and understood this guide
- [ ] Followed the coding standards
- [ ] Added appropriate tests
- [ ] Updated documentation if needed
- [ ] Ensured all tests pass
- [ ] Used descriptive commit messages
- [ ] Created a clear pull request description

## 🤝 Code of Conduct

We are committed to providing a welcoming and inclusive environment for all contributors. Please:

- Be respectful and considerate
- Focus on the code and technical issues
- Help others learn and grow
- Report any inappropriate behavior

## 📄 License

By contributing to VowVault, you agree that your contributions will be licensed under the same MIT License that covers the project.

---

Thank you for contributing to VowVault! Your contributions help make this project better for everyone. 🎉

If you have any questions about this guide, please open an issue or start a discussion.