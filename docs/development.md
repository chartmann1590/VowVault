# Development Guide

This guide provides comprehensive information for developers working on VowVault.

## 🚀 Development Setup

### Prerequisites

- Python 3.8+
- Git
- Docker (optional)
- Node.js 16+ (for frontend assets)

### Quick Start

1. **Clone the repository**
   ```bash
   git clone https://github.com/chartmann1590/VowVault.git
   cd VowVault
   ```

2. **Set up virtual environment**
   ```bash
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   ```

3. **Install dependencies**
   ```bash
   pip install -r requirements.txt
   pip install -r requirements-dev.txt
   ```

4. **Set up pre-commit hooks**
   ```bash
   pre-commit install
   ```

5. **Run the application**
   ```bash
   python run.py
   ```

## 🏗️ Project Structure

```
VowVault/
├── app/                    # Main application code
│   ├── __init__.py        # Flask app initialization
│   ├── models/            # Database models
│   ├── routes/            # Route handlers
│   ├── services/          # Business logic
│   ├── templates/         # HTML templates
│   └── static/            # Static assets
├── docs/                  # Documentation
├── tests/                 # Test suite
├── migrations/            # Database migrations
├── docker/                # Docker configuration
├── .github/               # GitHub workflows
├── requirements.txt       # Production dependencies
├── requirements-dev.txt   # Development dependencies
└── README.md             # Project overview
```

## 🔧 Development Tools

### Code Quality Tools

- **Black**: Code formatting
- **isort**: Import sorting
- **Flake8**: Linting
- **MyPy**: Type checking
- **Bandit**: Security analysis
- **Safety**: Dependency vulnerability scanning

### Running Quality Checks

```bash
# Format code
black app/ tests/

# Sort imports
isort app/ tests/

# Lint code
flake8 app/ tests/

# Type checking
mypy app/

# Security checks
bandit -r app/
safety check
```

### Pre-commit Hooks

Pre-commit hooks automatically run quality checks before each commit:

```bash
# Install hooks
pre-commit install

# Run manually
pre-commit run --all-files

# Run specific hook
pre-commit run black
```

## 🧪 Testing

### Test Structure

```
tests/
├── unit/                  # Unit tests
│   ├── test_models.py    # Model tests
│   ├── test_services.py  # Service tests
│   └── test_utils.py     # Utility tests
├── integration/           # Integration tests
│   ├── test_api.py       # API tests
│   └── test_auth.py      # Authentication tests
├── fixtures/              # Test data
│   ├── test_data.py      # Sample data
│   └── factories.py      # Data factories
└── conftest.py           # Test configuration
```

### Running Tests

```bash
# Run all tests
python -m pytest

# Run with coverage
python -m pytest --cov=app --cov-report=html

# Run specific test file
python -m pytest tests/unit/test_models.py

# Run tests in parallel
python -m pytest -n auto

# Run tests with verbose output
python -m pytest -v

# Run only failed tests
python -m pytest --lf
```

### Writing Tests

Follow these guidelines when writing tests:

- Use descriptive test names
- Test both success and failure cases
- Use fixtures for common test data
- Mock external dependencies
- Aim for good test coverage

Example test:

```python
import pytest
from app.models import Photo
from app.services import PhotoService

def test_photo_upload_success(client, auth_headers):
    """Test successful photo upload."""
    data = {
        'file': (b'fake-image-data', 'test.jpg'),
        'description': 'Test photo'
    }
    
    response = client.post('/upload', data=data, headers=auth_headers)
    
    assert response.status_code == 200
    assert 'photo_id' in response.json

def test_photo_upload_invalid_file(client, auth_headers):
    """Test photo upload with invalid file."""
    data = {
        'file': (b'invalid-data', 'test.txt'),
        'description': 'Test photo'
    }
    
    response = client.post('/upload', data=data, headers=auth_headers)
    
    assert response.status_code == 400
    assert 'Invalid file type' in response.json['error']
```

## 📚 Documentation

### Documentation Standards

- Use clear, concise language
- Include code examples
- Keep documentation up-to-date
- Use consistent formatting

### Building Documentation

```bash
# Install Sphinx
pip install sphinx sphinx-rtd-theme

# Build documentation
cd docs
make html

# View documentation
open _build/html/index.html
```

### API Documentation

API endpoints should be documented using docstrings:

```python
@app.route('/api/photos', methods=['GET'])
def get_photos():
    """
    Get all photos.
    
    ---
    get:
      summary: Retrieve all photos
      parameters:
        - name: page
          in: query
          description: Page number
          required: false
          schema:
            type: integer
            default: 1
        - name: per_page
          in: query
          description: Photos per page
          required: false
          schema:
            type: integer
            default: 20
      responses:
        200:
          description: List of photos
          content:
            application/json:
              schema:
                type: array
                items:
                  $ref: '#/components/schemas/Photo'
    """
    # Implementation here
```

## 🐳 Docker Development

### Development with Docker

```bash
# Build development image
docker build -f Dockerfile.dev -t vowvault:dev .

# Run development container
docker run -it --rm \
  -p 5000:5000 \
  -v $(pwd):/app \
  -v $(pwd)/uploads:/app/static/uploads \
  vowvault:dev

# Use docker-compose for development
docker-compose -f docker-compose.dev.yml up
```

### Docker Compose Development

Create `docker-compose.dev.yml`:

```yaml
version: '3.8'

services:
  app:
    build:
      context: .
      dockerfile: Dockerfile.dev
    ports:
      - "5000:5000"
    volumes:
      - .:/app
      - ./uploads:/app/static/uploads
    environment:
      - FLASK_ENV=development
      - FLASK_DEBUG=1
    command: python run.py

  db:
    image: postgres:13
    environment:
      POSTGRES_DB: vowvault_dev
      POSTGRES_USER: dev
      POSTGRES_PASSWORD: dev
    ports:
      - "5432:5432"
    volumes:
      - postgres_data:/var/lib/postgresql/data

volumes:
  postgres_data:
```

## 🔒 Security Development

### Security Best Practices

- Never commit secrets or API keys
- Use environment variables for configuration
- Validate all user inputs
- Implement proper authentication and authorization
- Use HTTPS in production
- Regular security audits

### Security Testing

```bash
# Run security checks
bandit -r app/ -f json -o bandit-report.json
safety check --json --output safety-report.json

# Check for known vulnerabilities
pip-audit
```

## 📊 Performance

### Performance Monitoring

- Use Flask-Profiler for development
- Monitor database query performance
- Implement caching where appropriate
- Use async operations for I/O-bound tasks

### Performance Testing

```bash
# Install performance testing tools
pip install locust

# Run load tests
locust -f tests/performance/locustfile.py
```

## 🚀 Deployment

### Environment Configuration

Use environment variables for configuration:

```bash
# .env file
FLASK_ENV=production
DATABASE_URL=postgresql://user:pass@localhost/vowvault
SECRET_KEY=your-secret-key
SSO_ENABLED=true
```

### Production Checklist

- [ ] All tests pass
- [ ] Security scan completed
- [ ] Performance tested
- [ ] Documentation updated
- [ ] Environment variables configured
- [ ] SSL certificates installed
- [ ] Backup strategy implemented
- [ ] Monitoring configured

## 🔄 Database Migrations

### Creating Migrations

```bash
# Generate migration
flask db migrate -m "Add user table"

# Apply migration
flask db upgrade

# Rollback migration
flask db downgrade
```

### Migration Best Practices

- Always backup before migrations
- Test migrations on staging first
- Use transactions for data migrations
- Document breaking changes
- Provide rollback scripts

## 📱 Frontend Development

### Asset Management

```bash
# Install frontend dependencies
npm install

# Build assets
npm run build

# Watch for changes
npm run watch
```

### CSS and JavaScript

- Use modern CSS features
- Implement responsive design
- Optimize for mobile devices
- Use progressive enhancement

## 🐛 Debugging

### Debug Tools

```python
# Use Python debugger
import pdb; pdb.set_trace()

# Use IPython debugger (better)
import ipdb; ipdb.set_trace()

# Flask debug mode
app.debug = True
```

### Logging

```python
import logging

logger = logging.getLogger(__name__)
logger.info("Processing photo upload")
logger.error("Upload failed", exc_info=True)
```

## 📋 Development Checklist

Before submitting code:

- [ ] Code follows style guidelines
- [ ] Tests written and passing
- [ ] Documentation updated
- [ ] Security considerations addressed
- [ ] Performance impact assessed
- [ ] Pre-commit hooks pass
- [ ] Code reviewed (if applicable)

## 🆘 Getting Help

### Resources

- [Flask Documentation](https://flask.palletsprojects.com/)
- [SQLAlchemy Documentation](https://docs.sqlalchemy.org/)
- [Python Testing with pytest](https://docs.pytest.org/)
- [GitHub Issues](https://github.com/chartmann1590/VowVault/issues)

### Asking Questions

When asking for help:

1. Be specific about your problem
2. Include relevant code and error messages
3. Describe what you've tried
4. Provide your environment details

---

Happy coding! 🎉