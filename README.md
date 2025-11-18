# #FahanieCares Website

The official website system for MP Atty. Sittie Fahanie S. Uy-Oyod's #FahanieCares initiative - Bringing Public Service Closer to You.

## Overview

The #FahanieCares website is a comprehensive digital platform designed to streamline constituent services, manage chapter operations, and track public service delivery. Built with Django and integrated with Notion for data management, it provides a robust solution for efficient public service administration.

## Features

### Core Functionality
- **Constituent Management**: Complete profiles, history tracking, and communication logs
- **Service Referral System**: End-to-end referral tracking with multi-agency coordination
- **Chapter Management**: Member registration, activity planning, and performance monitoring
- **Document Management**: Secure file storage with version control
- **Reporting & Analytics**: Real-time dashboards and custom report generation
- **Search & Filtering**: Advanced search capabilities across all modules
- **Notification System**: Multi-channel notifications (Email, SMS, In-app)

### Technical Features
- **Notion Integration**: Seamless sync with Notion databases
- **Role-Based Access Control**: Granular permissions system
- **Mobile Responsive**: Fully responsive design for all devices
- **Security**: Industry-standard security measures including MFA
- **Performance**: Optimized for high-traffic scenarios
- **Scalability**: Cloud-ready architecture

## Technology Stack

- **Backend**: Python 3.9+, Django 4.2+
- **Frontend**: HTML5, CSS3, JavaScript, TailwindCSS
- **Database**: PostgreSQL (all environments)
- **External Services**: Notion API, AWS S3, SendGrid
- **Deployment**: Docker, Nginx, Gunicorn
- **Monitoring**: New Relic, Sentry

## Project Structure

```
fahanie-cares/
├── src/                     # Django source code
│   ├── apps/
│   │   ├── core/
│   │   ├── users/
│   │   ├── constituents/
│   │   ├── referrals/
│   │   ├── chapters/
│   │   ├── documents/
│   │   ├── notifications/
│   │   ├── search/
│   │   └── dashboards/
│   ├── config/
│   ├── static/
│   ├── templates/
│   └── utils/
├── deployment/
├── docs/
├── testing/
├── training/
└── tasks/
```

## Installation

### Prerequisites
- Python 3.9 or higher
- PostgreSQL 13+
- Node.js 14+ (for frontend assets)
- Redis (for caching)

### Development Setup

1. Clone the repository:
```bash
git clone https://github.com/mpuyoyod/fahanie-cares.git
cd fahanie-cares
```

2. Create virtual environment:
```bash
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

3. Navigate to Django source directory and install dependencies:
```bash
cd src
pip install -r requirements.txt
```

4. Set up environment variables:
```bash
cp .env.example .env
# Edit .env with your configuration
```

5. Run migrations:
```bash
python manage.py migrate
```

6. Create superuser:
```bash
python manage.py createsuperuser
```

7. Load sample data (optional):
```bash
python manage.py loaddata fixtures/sample_data.json
```

8. Run development server:
```bash
python manage.py runserver 3000
```

Visit http://localhost:3000 to access the application.

## Configuration

### Environment Variables

Key environment variables in `.env`:

```env
# Django Settings
SECRET_KEY=your-secret-key
DEBUG=True
ALLOWED_HOSTS=localhost,127.0.0.1

# Database
DATABASE_URL=postgres://user:password@localhost/dbname

# Notion API
NOTION_API_KEY=your-notion-api-key
NOTION_CONSTITUENTS_DATABASE=database-id
NOTION_REFERRALS_DATABASE=database-id

# Email
EMAIL_HOST=smtp.sendgrid.net
EMAIL_PORT=587
EMAIL_HOST_USER=apikey
EMAIL_HOST_PASSWORD=your-sendgrid-api-key

# AWS S3 (for file storage)
AWS_ACCESS_KEY_ID=your-access-key
AWS_SECRET_ACCESS_KEY=your-secret-key
AWS_STORAGE_BUCKET_NAME=fahaniecares-files
```

## Usage

### Quick Start Guide

1. **Login**: Use your credentials at /login
2. **Dashboard**: View key metrics and recent activities
3. **Constituents**: Manage constituent profiles
4. **Referrals**: Create and track service referrals
5. **Reports**: Generate various reports
6. **Search**: Use global search for quick access

### User Roles

- **Administrator**: Full system access
- **Staff**: Operational functions
- **Chapter Coordinator**: Chapter management
- **Public User**: Limited access for requests

## Development

### Running Tests

```bash
# Run all tests
python manage.py test

# Run specific app tests
python manage.py test apps.referrals

# Run with coverage
coverage run --source='.' manage.py test
coverage report
```

### Code Style

Follow PEP 8 guidelines. Use automated formatting:

```bash
# Install development dependencies
pip install black flake8 isort

# Format code
black .
isort .
flake8 .
```

### Database Migrations

```bash
# Create migrations
python manage.py makemigrations

# Apply migrations
python manage.py migrate

# Check migration status
python manage.py showmigrations
```

## Deployment

### Production Deployment

1. Set production environment variables
2. Collect static files:
```bash
python manage.py collectstatic
```

3. Run deployment script:
```bash
./deployment/scripts/deploy.sh
```

### Docker Deployment

```bash
# Build image
docker build -t fahaniecares .

# Run container (development - port 3000)
docker run -p 3000:8000 fahaniecares

# Run container (production - port 8000)
docker run -p 8000:8000 fahaniecares
```

## API Documentation

API documentation is available at `/api/docs/` when running the application.

### Key Endpoints

- `/api/constituents/` - Constituent management
- `/api/referrals/` - Referral operations
- `/api/chapters/` - Chapter information
- `/api/reports/` - Report generation

## Contributing

1. Fork the repository
2. Create a feature branch
3. Commit your changes
4. Push to the branch
5. Create a Pull Request

### Commit Guidelines

Use conventional commits:
- `feat:` New feature
- `fix:` Bug fix
- `docs:` Documentation
- `style:` Code style
- `refactor:` Code refactoring
- `test:` Tests
- `chore:` Maintenance

## Support

### Getting Help

- **Documentation**: `/docs/`
- **User Guide**: `/training/user_guide.md`
- **Support Email**: support@fahaniecares.gov.ph
- **Issue Tracker**: GitHub Issues

### Common Issues

See `docs/troubleshooting.md` for common issues and solutions.

## Security

### Reporting Security Issues

Please report security vulnerabilities to: security@fahaniecares.gov.ph

### Security Features

- HTTPS enforcement
- CSRF protection
- XSS prevention
- SQL injection protection
- Rate limiting
- Session security

## License

This project is proprietary software. All rights reserved.

## Acknowledgments

- Development Team
- MP Atty. Sittie Fahanie S. Uy-Oyod's Office
- Beta Testers and Early Users

---

*Version: 1.0.0*  
*Last Updated: January 2025*