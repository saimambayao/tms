# Fahanie Cares Django Project Structure

Below is the comprehensive directory structure for the #FahanieCares website following the reorganization plan:

```
fahanie-cares/
├── .env                     # Environment variables (gitignored)
├── .env.example             # Example environment file
├── .gitignore               # Git ignore file
├── README.md                # Main project documentation
├── CLAUDE.md                # AI assistant instructions
├── docker-compose.yml       # Default development docker-compose
│
├── src/                     # Django source code (renamed from fahanie_cares_django)
│   ├── requirements.txt     # Python dependencies
│   ├── manage.py            # Django management script
│   │
│   ├── config/              # Project configuration
│   │   ├── __init__.py
│   │   ├── asgi.py          # ASGI configuration
│   │   ├── settings/        # Settings modules
│   │   │   ├── __init__.py
│   │   │   ├── base.py      # Base settings
│   │   │   ├── development.py   # Development settings
│   │   │   └── production.py    # Production settings
│   │   ├── urls.py          # Main URL configuration
│   │   └── wsgi.py          # WSGI configuration
│   │
│   ├── static/              # Static files (CSS, JS, images)
│   │   ├── css/
│   │   │   ├── output.css   # Compiled Tailwind CSS
│   │   │   └── input.css    # Tailwind source
│   │   ├── js/
│   │   │   └── main.js      # Main JavaScript file
│   │   ├── images/
│   │   │   ├── logo.png
│   │   │   └── favicon.ico
│   │   └── admin/           # Admin static customizations
│   │
│   ├── media/               # User-uploaded media (gitignored)
│   │
│   ├── templates/           # Project-wide templates
│   │   ├── admin/           # Admin customization templates
│   │   ├── base/
│   │   │   ├── base.html    # Base template
│   │   │   └── mobile_base.html
│   │   ├── components/      # Reusable template components
│   │   │   ├── atoms/
│   │   │   ├── molecules/
│   │   │   ├── organisms/
│   │   │   └── navigation/
│   │   └── core/            # Core app templates
│   │
│   ├── apps/                # Django applications
│   │   ├── core/            # Core application (shared functionality)
│   │   ├── __init__.py
│   │   ├── admin.py
│   │   ├── apps.py
│   │   ├── forms.py
│   │   ├── managers.py
│   │   ├── migrations/
│   │   ├── models.py
│   │   ├── tests/
│   │   ├── urls.py
│   │   └── views.py
│   │   └── templates/
│   │       └── core/
│   │           ├── home.html
│   │           ├── about.html
│   │           ├── contact.html
│   │           └── news.html
│   │
│   ├── users/               # User management
│   │   ├── __init__.py
│   │   ├── admin.py
│   │   ├── apps.py
│   │   ├── forms.py
│   │   ├── managers.py
│   │   ├── migrations/
│   │   ├── models.py        # Custom user model
│   │   ├── tests/
│   │   ├── urls.py
│   │   ├── views.py
│   │   └── templates/
│   │       └── users/
│   │           ├── login.html
│   │           ├── signup.html
│   │           ├── profile.html
│   │           └── password_reset.html
│   │
│   ├── constituents/        # Constituent management module
│   │   ├── __init__.py
│   │   ├── admin.py
│   │   ├── apps.py
│   │   ├── forms.py
│   │   ├── migrations/
│   │   ├── models.py
│   │   ├── tests/
│   │   ├── urls.py
│   │   ├── views.py
│   │   └── templates/
│   │       └── constituents/
│   │           ├── dashboard.html
│   │           ├── profile_detail.html
│   │           ├── profile_edit.html
│   │           └── list.html
│   │
│   ├── referrals/           # Service referral system module
│   │   ├── __init__.py
│   │   ├── admin.py
│   │   ├── apps.py
│   │   ├── forms.py
│   │   ├── migrations/
│   │   ├── models.py
│   │   ├── tests/
│   │   ├── urls.py
│   │   ├── views.py
│   │   └── templates/
│   │       └── referrals/
│   │           ├── service_directory.html
│   │           ├── request_form.html
│   │           ├── case_detail.html
│   │           ├── case_list.html
│   │           └── agency_portal.html
│   │
│   ├── chapters/            # Chapter management module
│   │   ├── __init__.py
│   │   ├── admin.py
│   │   ├── apps.py
│   │   ├── forms.py
│   │   ├── migrations/
│   │   ├── models.py
│   │   ├── tests/
│   │   ├── urls.py
│   │   ├── views.py
│   │   └── templates/
│   │       └── chapters/
│   │           ├── chapter_list.html
│   │           ├── chapter_detail.html
│   │           ├── member_list.html
│   │           ├── member_detail.html
│   │           └── activity_calendar.html
│   │
│   ├── services/            # Direct service module
│   │   ├── __init__.py
│   │   ├── admin.py
│   │   ├── apps.py
│   │   ├── forms.py
│   │   ├── migrations/
│   │   ├── models.py
│   │   ├── tests/
│   │   ├── urls.py
│   │   ├── views.py
│   │   └── templates/
│   │       └── services/
│   │           ├── service_catalog.html
│   │           ├── application_form.html
│   │           ├── application_detail.html
│   │           ├── resource_management.html
│   │           └── mobile_service.html
│   │
│   ├── communications/      # Communication module
│   │   ├── __init__.py
│   │   ├── admin.py
│   │   ├── apps.py
│   │   ├── forms.py
│   │   ├── migrations/
│   │   ├── models.py
│   │   ├── tests/
│   │   ├── urls.py
│   │   ├── views.py
│   │   └── templates/
│   │       └── communications/
│   │           ├── campaign_list.html
│   │           ├── campaign_detail.html
│   │           ├── message_templates.html
│   │           ├── feedback_form.html
│   │           └── analytics.html
│   │
│   ├── analytics/           # Analytics and reporting module
│   │   ├── __init__.py
│   │   ├── admin.py
│   │   ├── apps.py
│   │   ├── forms.py
│   │   ├── migrations/
│   │   ├── models.py
│   │   ├── tests/
│   │   ├── urls.py
│   │   ├── views.py
│   │   └── templates/
│   │       └── analytics/
│   │           ├── dashboard.html
│   │           ├── performance_metrics.html
│   │           ├── impact_assessment.html
│   │           └── reports.html
│   │
│   └── parliamentary/       # Parliamentary work module
│       ├── __init__.py
│       ├── admin.py
│       ├── apps.py
│       ├── forms.py
│       ├── migrations/
│       ├── models.py
│       ├── tests/
│       ├── urls.py
│       ├── views.py
│       └── templates/
│           └── parliamentary/
│               ├── legislation_tracker.html
│               ├── oversight_activities.html
│               ├── public_hearings.html
│               └── resources.html
│
├── api/                     # API functionality
│   ├── __init__.py
│   ├── routers.py           # DRF routers
│   ├── urls.py              # API URLs
│   ├── authentication/      # API authentication
│   │   ├── __init__.py
│   │   ├── serializers.py
│   │   └── views.py
│   └── v1/                  # API version
│       ├── __init__.py
│       ├── constituents/
│       │   ├── __init__.py
│       │   ├── serializers.py
│       │   └── views.py
│       ├── referrals/
│       │   ├── __init__.py
│       │   ├── serializers.py
│       │   └── views.py
│       ├── chapters/
│       │   ├── __init__.py
│       │   ├── serializers.py
│       │   └── views.py
│       └── services/
│           ├── __init__.py
│           ├── serializers.py
│           └── views.py
│
├── utils/                   # Utility modules
│   ├── __init__.py
│   ├── notion/              # Notion API integration
│   │   ├── __init__.py
│   │   ├── client.py        # Notion API client
│   │   ├── database.py      # Database operations
│   │   ├── page.py          # Page operations
│   │   └── sync.py          # Synchronization utilities
│   ├── communication/       # Communication utilities
│   │   ├── __init__.py
│   │   ├── email.py         # Email utilities
│   │   └── sms.py           # SMS utilities
│   └── helpers/             # Helper functions
│       ├── __init__.py
│       ├── data_processing.py
│       ├── file_handling.py
│       └── geo_utils.py
│
├── docs/                    # Documentation
│   ├── architecture/        # Architecture documentation
│   ├── api/                 # API documentation
│   ├── deployment/          # Deployment guides
│   └── user_manuals/        # User manuals
│
│   └── utils/               # Utility modules
│       ├── __init__.py
│       └── notifications.py # Notification utilities
│
├── deployment/              # All deployment configurations
│   ├── docker/              # Docker-related files
│   │   ├── Dockerfile               
│   │   ├── Dockerfile.frontend      
│   │   ├── Dockerfile.production    
│   │   └── docker-compose/  # Environment-specific compose files
│   │       ├── development.yml      
│   │       ├── production.yml       
│   │       ├── test.yml            
│   │       └── coolify.yml         
│   ├── nginx/               # Nginx configurations
│   │   ├── nginx.conf               
│   │   ├── nginx-dev.conf          
│   │   └── nginx-coolify.conf      
│   ├── scripts/             # Deployment scripts
│   │   ├── deploy.sh
│   │   ├── backup_database.sh
│   │   ├── backup_media.sh
│   │   └── ssl_monitor.py
│   └── ssl/                 # SSL configurations
│       ├── setup_ssl.sh
│       └── ssl_security.conf
│
├── docs/                    # All documentation
│   ├── architecture/        # Architecture documentation
│   │   ├── folder_reorganization_plan.md
│   │   ├── technical_architecture.md
│   │   ├── notion_fallback_architecture.md
│   │   └── rbac_architecture_diagram.md
│   ├── user/                # User documentation
│   │   ├── USER_MANUAL.txt
│   │   └── announcement_management_guide.md
│   ├── developer/           # Developer documentation
│   │   ├── API_DOCUMENTATION.txt
│   │   └── DEVELOPER_MANUAL.txt
│   ├── deployment/          # Deployment guides
│   │   ├── production_deployment_guide.md
│   │   ├── coolify_deployment_execution.md
│   │   └── DEPLOYMENT_CHECKLIST.md
│   └── project-management/  # Project planning docs
│       └── tasks/
│
├── scripts/                 # Development scripts
│   ├── local/               # Local development scripts
│   │   ├── run_local.sh            
│   │   ├── run_local_windows.sh    
│   │   └── push_to_github.sh
│   └── setup/               # Setup and data scripts
│       └── create_sample_data.py
│
├── tests/                   # Integration test configurations
├── archive/                 # Archived/deprecated code
└── .github/                 # GitHub Actions workflows (if needed)
```

## Core Components Explanation

### 1. Project Configuration (`config/`)

This directory contains all Django project settings and configuration:

- **settings/**: Split settings for different environments (base, development, production, testing)
- **urls.py**: Main URL configuration
- **wsgi.py/asgi.py**: Web server configuration for deployment

### 2. Applications (`apps/`)

The project is organized into modular applications based on the PRD's module specifications:

- **core/**: Essential shared functionality, including the public-facing portal
- **users/**: Custom user model and authentication
- **constituents/**: Constituent profile and case management
- **referrals/**: Service referral system
- **chapters/**: Chapter management and membership
- **services/**: Direct service delivery
- **communications/**: Multi-channel communication system
- **analytics/**: Reporting and dashboards
- **parliamentary/**: MP's legislative and oversight activities

### 3. API (`api/`)

Django REST Framework implementation for Notion API integration:

- **v1/**: First API version with endpoints for each module
- **authentication/**: API authentication and permission classes
- **routers.py**: API endpoint routing

### 4. Notion Integration (`utils/notion/`)

Specialized utilities for interacting with Notion as the primary database:

- **client.py**: Configures and manages the Notion API client
- **database.py**: Database operations (query, create, update)
- **page.py**: Page operations (create, retrieve, update)
- **sync.py**: Synchronization utilities for keeping Django and Notion data in sync

### 5. Templates and Static Files

- **templates/**: Django templates organized by application
- **static/**: Static assets with TailwindCSS for styling

### 6. Media Files

- **media/**: User-uploaded content (gitignored)

### 7. Documentation and Scripts

- **docs/**: Comprehensive documentation
- **scripts/**: Utility scripts for deployment, data migration, etc.

## Key Design Principles

1. **Modularity**: Each functional area has its own Django application
2. **Separation of Concerns**: Clear boundaries between components
3. **DRY (Don't Repeat Yourself)**: Common functionality in shared modules
4. **RESTful API Design**: Consistent API patterns for all modules
5. **Notion-First Architecture**: Optimized for using Notion as the primary database

## Development Workflow

1. Set up the project using the structure above
2. Implement the base infrastructure and Notion integration first
3. Develop core modules (users, constituents, referrals) next
4. Add additional modules based on priority
5. Implement analytics and reporting last

Each module includes its own models, views, templates, and tests for maximum independence while maintaining cohesion through shared utilities and the core application.

## Reorganized Structure Benefits

After the reorganization from `fahanie_cares_django/` to `src/`:

1. **Cleaner Root Directory**: The root now contains only essential configuration files and documentation.

2. **Better Separation of Concerns**: 
   - Source code in `src/`
   - Deployment configurations in `deployment/`
   - Documentation in `docs/`
   - Development scripts in `scripts/`

3. **Improved Deployment Workflow**: All Docker and deployment configurations are consolidated under `deployment/`, making it easier to manage different environments.

4. **Organized Documentation**: Documentation is categorized by type (architecture, user, developer, deployment) for easier navigation.

5. **Standard Django Practice**: Having the Django project in a `src/` directory is a common pattern that makes the project structure more recognizable to Django developers.

## Migration Notes

When migrating from the old structure to the new one, update all references:
- Docker build contexts: Change from `./fahanie_cares_django` to `./src`
- Shell scripts: Update paths to point to `src/` instead of `fahanie_cares_django/`
- Documentation: Update any path references in documentation files