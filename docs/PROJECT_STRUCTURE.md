# BM Parliament Project Structure

This document provides a comprehensive overview of the project directory structure after the reorganization completed on November 19, 2024.

## Root Directory Structure

```
bmparliament/
├── .env*                          # Environment configuration files
├── .github/                       # GitHub workflows and actions
├── .gitignore                     # Git ignore rules
├── .vscode/                       # VS Code settings
├── CLAUDE.md                      # AI assistant instructions
├── README.md                      # Main project documentation
├── Procfile                       # Process configuration for deployment
├── runtime.txt                    # Python runtime specification
├── railway.json                   # Railway deployment config
├── docker-compose*.yml            # Docker orchestration files
├── package.json                   # Node.js dependencies (TailwindCSS)
├── archive/                       # Deprecated and old files
├── deployment/                    # Deployment configurations and scripts
├── docs/                          # All project documentation
├── media/                         # User-uploaded media files
├── node_modules/                  # Node.js packages (gitignored)
├── scripts/                       # Utility scripts
├── src/                           # Main Django application source code
├── testing/                       # Test scripts and test plans
├── training/                      # User training materials
└── venv/                          # Python virtual environment (gitignored)
```

## Archive Directory

**Purpose**: Historical files no longer in active use but kept for reference.

```
archive/
├── ONE_COMMAND_FIX.txt           # Old quick fix instructions
├── FC_DB.session.sql             # Old database session file
├── index.html                    # Legacy static page
├── registration_response.html    # Legacy response page
└── fahanie_cares_prototype/      # Original FahanieCares prototype files
```

## Deployment Directory

**Purpose**: All deployment-related configurations, scripts, and Docker files.

```
deployment/
├── .env                          # Deployment environment variables
├── entrypoint.sh                 # Docker container entrypoint (development)
├── entrypoint-production.sh      # Docker container entrypoint (production)
├── cloudfront-config.json        # AWS CloudFront CDN configuration
├── docker/                       # Docker configurations
│   ├── Dockerfile                # Main production Dockerfile
│   ├── Dockerfile.coolify        # Coolify-specific Dockerfile
│   ├── Dockerfile.production     # Production-optimized Dockerfile
│   └── docker-compose/           # Docker Compose configurations
│       ├── coolify.yml
│       ├── coolify-django.yml
│       ├── production.yml
│       ├── frontend.yml
│       └── test.yml
├── nginx/                        # Nginx web server configurations
│   ├── nginx.conf                # Main Nginx configuration
│   └── nginx-coolify.conf        # Coolify-specific Nginx config
├── ssl/                          # SSL/TLS certificate management
│   ├── README.md
│   ├── setup_ssl.sh
│   ├── verify_ssl.sh
│   ├── ssl_security.conf
│   ├── ssl-setup.sh
│   ├── ssl-monitor.py
│   └── docker-compose.ssl.yml
└── scripts/                      # Deployment and maintenance scripts
    ├── deploy.sh                 # Main deployment script
    ├── deploy-css-fix.sh         # CSS cache fix deployment
    ├── deploy-radio-button-fix.sh
    ├── deploy-registration-fixes.sh
    ├── deploy-with-cache-invalidation.sh
    ├── fix-css-cache-now.sh
    ├── production-css-fix.sh
    ├── PRODUCTION_FIX_NOW.sh
    ├── verify-production-deployment.sh
    ├── rollback.sh               # Deployment rollback
    ├── backup_database.sh        # Database backup
    ├── backup_media.sh           # Media files backup
    ├── verify_backups.sh         # Verify backup integrity
    ├── performance_benchmark.sh   # Performance testing
    ├── daily_operations.sh       # Daily maintenance tasks
    ├── weekly_maintenance.sh     # Weekly maintenance tasks
    ├── launch_sequence.sh        # Launch checklist automation
    ├── pre_launch_checklist.sh   # Pre-launch verification
    ├── load_test.py              # Load testing script
    ├── generate_api_docs.py      # API documentation generation
    ├── ssl_cron_setup.sh         # SSL renewal cron job
    └── ssl_monitor.py            # SSL certificate monitoring
```

## Documentation Directory

**Purpose**: All project documentation, guides, and architectural documents.

```
docs/
├── README.md                     # Documentation index
├── CLAUDE.md                     # AI assistant context (duplicate)
├── TEST_REPORT.md                # Testing results and reports
├── RADIO_BUTTON_FIX_SUMMARY.md   # Radio button fix documentation
├── AUTOMATION_IMPLEMENTATION_PLAN.md
├── DOCKER_README.md              # Docker usage guide
├── DOCKER_REBUILD_INSTRUCTIONS.md
├── LOCAL_SETUP_GUIDE.md          # Local development setup
├── PRAGMATIC_AUTOMATION_PLAN.md
├── PROJECT_STRUCTURE.md          # This file
├── monitoring_guide.md           # System monitoring guide
├── portal_approach_comparison_report.md
├── rbac_implementation_plan.md   # Role-based access control plan
├── running_django_manually.md    # Manual Django execution guide
├── sms_otp_cost_documentation.md
├── sms_otp_payment_implementation.md
├── support_procedures.md         # User support procedures
├── ui_mockups_by_role.md
├── unified_interface_evaluation_report.md
├── user_role_plan_and_design.md
├── architecture/                 # Architecture documentation
│   ├── django_project_structure.md
│   ├── folder_reorganization_plan.md
│   ├── notion_fallback_architecture.md
│   ├── rbac_architecture_diagram.md
│   ├── reorganization_summary.md
│   ├── tailwindcss_integration_analysis_report.md
│   ├── technical_architecture.md
│   └── unified_interface_architecture.md
├── deployment/                   # Deployment guides
│   ├── COOLIFY_DEPLOYMENT_GUIDE.md
│   ├── DEPLOYMENT_CHECKLIST.md
│   ├── IMMEDIATE_CDN_FIX.md
│   ├── MEMBER_REGISTRATION_UPDATE_SUMMARY.md
│   ├── POSTGRESQL_MIGRATION_GUIDE.md
│   ├── PRODUCTION_DEPLOYMENT_NOW.md
│   ├── PRODUCTION_QUICKSTART.md
│   ├── PRODUCTION_READINESS_REPORT.md
│   ├── PRODUCTION_REGISTRATION_FIX_SUMMARY.md
│   ├── REGISTRATION_FIX_DEPLOYMENT.md
│   ├── SYSTEMATIC_CACHE_SOLUTION.md
│   ├── coolify_deployment_execution.md
│   ├── css_production_fix.md
│   ├── deployment_configuration.md
│   ├── deployment_configuration_report.md
│   ├── django_static_files_deployment_solution.md
│   ├── docker_configuration_report.md
│   ├── docker_final_test_report.md
│   ├── postgresql_only_migration.md
│   └── production_deployment_guide.md
├── developer/                    # Developer documentation
│   ├── DEVELOPER_MANUAL.txt
│   ├── implementation_plan.md
│   └── radio_button_validation_fix.md
├── project-management/           # Project management docs
│   └── prd.txt                   # Product Requirements Document
├── ui/                           # UI/UX documentation
│   └── (UI mockups and designs)
└── user/                         # End-user documentation
    ├── USER_MANUAL.txt
    └── announcement_management_guide.md
```

## Scripts Directory

**Purpose**: Utility scripts for development, database management, and system utilities.

```
scripts/
├── README.md                     # Scripts documentation
├── local/                        # Local development scripts
│   ├── push_to_github.sh
│   ├── run_local.sh
│   ├── run_local_modified.sh
│   └── run_local_windows.sh
├── utilities/                    # Python utility scripts
│   ├── execute_unified_interface.py
│   ├── update_member_status.py
│   └── update_program_public_status.py
└── windows/                      # Windows PowerShell scripts
    ├── activate_and_run.ps1
    ├── install-pyenv-win.ps1
    ├── local_setup.ps1
    ├── run_migrations.ps1
    ├── run_server.ps1
    └── start_local.ps1
```

## Source Directory (src/)

**Purpose**: Main Django application source code.

```
src/
├── manage.py                     # Django management script
├── requirements.txt              # Python dependencies
├── package.json                  # Node.js dependencies (TailwindCSS)
├── tailwind.config.js            # TailwindCSS configuration
├── db.sqlite3                    # SQLite database (development)
├── .env*                         # Environment configuration
├── apps/                         # Django applications
│   ├── analytics/                # Analytics and reporting
│   ├── chapters/                 # Chapter management
│   ├── communications/           # Notification system
│   ├── constituents/             # Constituent management
│   ├── cooperatives/             # Cooperative management
│   ├── core/                     # Core functionality
│   ├── documents/                # Document management
│   ├── notifications/            # Notification system
│   ├── referrals/                # Service referral system
│   ├── services/                 # Public services
│   ├── staff/                    # Staff management
│   ├── unified_db/               # Unified database interface
│   └── users/                    # User authentication and RBAC
├── config/                       # Django configuration
│   ├── __init__.py
│   ├── celery.py                 # Celery task queue config
│   ├── urls.py                   # URL routing
│   ├── wsgi.py                   # WSGI configuration
│   └── settings/                 # Settings by environment
│       ├── base.py               # Base settings
│       ├── development.py        # Development settings
│       └── production.py         # Production settings
├── locale/                       # Internationalization files
│   └── tl/                       # Tagalog translations
├── management/                   # Custom Django management commands
├── media/                        # User-uploaded files
├── scripts/                      # Django-specific utility scripts
│   ├── backup_database.py
│   ├── check_media_production.py
│   ├── create_sample_data.py
│   ├── create_staff_final.py
│   ├── grant_developer_admin_access.py
│   ├── staff_profile_summary.py
│   ├── verify_admin_access.py
│   └── archive/                  # Old/deprecated scripts
├── static/                       # Static files (CSS, JS, images)
│   ├── css/
│   ├── images/
│   └── HeroB/
├── templates/                    # Django templates
│   ├── admin/                    # Admin interface templates
│   ├── base/                     # Base templates
│   ├── components/               # Reusable UI components
│   │   ├── atoms/                # Basic UI elements
│   │   ├── molecules/            # Composite components
│   │   ├── organisms/            # Complex sections
│   │   ├── behaviors/            # Alpine.js behaviors
│   │   ├── design-system/        # Design system docs
│   │   ├── examples/             # Component examples
│   │   ├── navigation/           # Navigation components
│   │   └── widgets/              # Custom widgets
│   ├── constituents/             # Constituent templates
│   ├── core/                     # Core app templates
│   ├── emails/                   # Email templates
│   ├── mobile/                   # Mobile-specific templates
│   ├── referrals/                # Referral system templates
│   ├── services/                 # Service templates
│   └── users/                    # User management templates
├── tests/                        # Test files
│   ├── test_database_integration.py
│   ├── test_e2e_database_journeys.py
│   ├── test_e2e_user_journeys.py
│   ├── test_integration.py
│   ├── test_lgbtq_sector.py
│   ├── test_production_security.py
│   ├── test_registration_e2e.py
│   └── test_settings.py
├── test_media/                   # Test media files
├── unified_db/                   # Unified database utilities
├── utils/                        # Shared utilities
│   └── notifications.py
└── venv/                         # Virtual environment (gitignored)
```

## Testing Directory

**Purpose**: Integration tests, end-to-end tests, and test documentation.

```
testing/
├── README.md                     # Testing documentation
├── test_plan.md                  # Comprehensive test plan
├── run_tests.sh                  # Test runner script
├── check_program_status.py       # Program status verification
├── check_status.py               # System health checks
├── test_cancer_dialysis_sector.py
├── test_madaris_sector.py
├── simple_test_cancer_dialysis.py
├── simple_test_madaris.py
├── test_pandas_django.py
└── test_registration_flow.py    # Registration E2E tests
```

## Training Directory

**Purpose**: User training materials and guides.

```
training/
├── quick_reference.md            # Quick reference guide
├── training_plan.md              # Training program plan
└── user_guide.md                 # Comprehensive user guide
```

## Key Organizational Principles

### 1. Separation of Concerns
- **Source code** (`src/`) - Only Django application code
- **Documentation** (`docs/`) - All documentation in one place
- **Scripts** (`scripts/`, `deployment/scripts/`) - Organized by purpose
- **Tests** (`testing/`, `src/tests/`) - Integration vs unit tests

### 2. Environment-Specific Files
- Root `.env*` files - Docker and deployment configuration
- `src/.env*` files - Django application configuration
- Separate Docker Compose files for different environments

### 3. Clean Root Directory
The root directory contains only:
- Essential configuration files (`.env`, `docker-compose.yml`, `package.json`)
- Primary documentation (`README.md`, `CLAUDE.md`)
- Core directories

### 4. Django Best Practices
The `src/` directory follows Django conventions:
- Apps in `apps/` directory
- Settings split by environment in `config/settings/`
- Templates organized by component (Atomic Design)
- Tests alongside source code in `tests/`

## File Location Guide

| File Type | Location | Examples |
|-----------|----------|----------|
| Django apps | `src/apps/` | `constituents/`, `referrals/` |
| Configuration | `src/config/` | `settings/`, `urls.py` |
| Templates | `src/templates/` | `base/`, `components/` |
| Static files | `src/static/` | `css/`, `images/` |
| Django scripts | `src/scripts/` | `create_sample_data.py` |
| Unit tests | `src/tests/` | `test_integration.py` |
| E2E tests | `testing/` | `test_registration_flow.py` |
| Utilities | `scripts/utilities/` | `update_member_status.py` |
| Windows scripts | `scripts/windows/` | `*.ps1` files |
| Deployment | `deployment/` | Docker, Nginx, SSL configs |
| Documentation | `docs/` | All `.md` files |
| Archives | `archive/` | Old/deprecated files |

## Navigation Tips

### Finding Files
```bash
# Find all Python test files
find . -name "test_*.py"

# Find all deployment scripts
ls deployment/scripts/

# Find all documentation
ls docs/

# Find Django management commands
ls src/apps/*/management/commands/
```

### Common Paths
- Main Django code: `src/apps/`
- User documentation: `docs/user/`
- Developer docs: `docs/developer/`
- Deployment guides: `docs/deployment/`
- Test files: `testing/` and `src/tests/`

## Version History

- **November 19, 2024**: Major reorganization
  - Consolidated all documentation into `docs/`
  - Organized scripts by type and platform
  - Cleaned up `src/` directory
  - Moved deployment files to `deployment/`
  - Created proper directory structure

---

*Last Updated: November 19, 2024*
*Version: 2.0*
