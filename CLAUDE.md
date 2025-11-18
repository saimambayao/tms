# CLAUDE.md

This file provides guidance to Claude Code when working with the #FahanieCares portal.

## Project Overview

The #FahanieCares website is a Django-based web application serving as the digital platform for MP Atty. Sittie Fahanie S. Uy-Oyod's public service initiative. The system uses PostgreSQL as its primary database, leveraging Django's robust ORM capabilities to deliver the #FahanieCares mission of "Bringing Public Service Closer to You."

Key features include:
- Constituent management and service referral system
- Chapter membership and organization  
- Direct service delivery tracking
- Parliamentary work documentation
- Analytics and reporting

## Development Workflow

### Task Management
- Use `TodoWrite` and `TodoRead` tools for multi-step tasks
- Update todo status as `in_progress`, `completed`, or `cancelled`  
- Break down complex tasks into smaller, trackable subtasks

### Code Quality Standards
- Follow Django best practices and PEP 8
- Test ALL code before marking tasks complete
- Document functions, classes, and architectural decisions
- Follow DRY principles and maintain consistent structure

### Git Workflow

All commits must be attributed to "#FahanieCares Development Team":
```bash
git config user.name "#FahanieCares Development Team"
git config user.email "dev@fahaniecares.ph"
```

**Security**: Always check for secrets before committing. Never commit `.env` files or sensitive data.

## Technology Stack

- **Backend**: Python/Django 5.2+ with PostgreSQL
- **Frontend**: Django Templates with TailwindCSS  
- **Cache**: Redis
- **Infrastructure**: Docker, AWS (EC2, S3, CloudFront)

## Docker Development Workflow (Recommended)

**One-Command Setup**: Run the complete portal with one command:
```bash
docker-compose up -d
```

This automatically:
- Builds all Docker images (PostgreSQL, Redis, Django, Nginx)
- Runs database migrations
- Compiles TailwindCSS
- Sets up user roles
- Starts the portal at http://localhost:3000

### Real-Time Development
**Code changes sync immediately** - no rebuild needed:
- **Python/Django changes**: Auto-reload, visible immediately
- **Template changes**: Refresh browser  
- **CSS changes**: Hard refresh (Ctrl+F5)

### Updating Docker Environment

**For most code changes**: No command needed, just refresh browser.

**When dependencies change** (requirements.txt, package.json):
```bash
docker-compose up -d --build
```

**For service restarts** (configuration changes):
```bash
docker-compose restart
```

**Complete reset** (fresh start with clean volumes):
```bash
docker-compose down -v && docker-compose up -d
```

### Common Docker Commands
```bash
# View logs
docker-compose logs -f web

# Run Django commands inside container
docker-compose exec web python manage.py migrate
docker-compose exec web python manage.py createsuperuser
docker-compose exec web python manage.py test

# Rebuild TailwindCSS
docker-compose exec web npm run build-css

# Stop all services
docker-compose down
```

## Manual Development (Alternative)

**Port Usage**: Always use port 3000 for development.

```bash
# Navigate to Django source directory  
cd src/

# Activate virtual environment
source venv/bin/activate

# Install dependencies
pip3 install -r requirements.txt

# Run development server
python3 manage.py runserver 3000

# Common Django commands
python3 manage.py migrate
python3 manage.py test
python3 manage.py createsuperuser
```

## Project Architecture

### Core Apps
1. **core**: Base functionality and public pages
2. **users**: Authentication and user models  
3. **constituents**: Constituent profiles and management
4. **referrals**: Service referral system and case management
5. **chapters**: Chapter membership and organization

### Settings Organization
- `config/settings/base.py`: Common settings
- `config/settings/development.py`: Development settings
- `config/settings/production.py`: Production settings

### Database
- **PostgreSQL** with Django ORM
- **Redis** for caching and sessions
- Models in `apps/*/models.py`
- Business logic in `apps/*/services.py`

### URL Structure
- `/admin/` - Django admin interface
- `/accounts/` - User authentication
- `/staff/referrals/` - Staff management
- Apps mount at root level for clean URLs

## Testing

Run all tests:
```bash
python3 manage.py test
# Or in Docker:
docker-compose exec web python manage.py test
```

Run specific app tests:
```bash
python3 manage.py test apps.referrals
```

## Component Library System

The project uses Atomic Design principles with TailwindCSS and Alpine.js.

### Components Structure
```
templates/components/
├── atoms/           # Basic elements (button.html, badge.html)
├── molecules/       # Combinations (card.html, empty_state.html)  
├── organisms/       # Complex sections (card_grid.html)
├── behaviors/       # Alpine.js behaviors
└── navigation/      # Headers, footers
```

### Common Components

**Button**:
```django
{% include 'components/atoms/button.html' with variant='primary' text='Click Me' icon='fas fa-check' %}
```

**Card**:
```django
{% include 'components/molecules/card.html' with title='Title' description='Description' %}
```

**Badge**:
```django
{% include 'components/atoms/badge.html' with variant='success' text='Active' %}
```

### Alpine.js Behaviors
Available in `components/behaviors/common_behaviors.html`:
- `x-data="modal()"` - Modal dialogs
- `x-data="dropdown()"` - Dropdown menus
- `x-data="formValidation()"` - Form validation
- `x-data="search()"` - Search functionality

## Icon System

**Use Font Awesome 6 consistently** - never use placeholder images for UI elements.

### Standard Icons
```html
<!-- Actions -->
<i class="fas fa-edit"></i>          <!-- Edit -->
<i class="fas fa-trash"></i>         <!-- Delete -->
<i class="fas fa-download"></i>      <!-- Download -->

<!-- Status -->
<i class="fas fa-check text-green-600"></i>      <!-- Success -->
<i class="fas fa-times text-red-600"></i>        <!-- Error -->
<i class="fas fa-clock text-yellow-600"></i>     <!-- Pending -->

<!-- Documents -->
<i class="fas fa-certificate text-blue-600"></i>  <!-- Certificate -->
<i class="fas fa-id-card text-green-600"></i>     <!-- ID -->
<i class="fas fa-upload text-primary-600"></i>    <!-- Upload -->

<!-- Services -->
<i class="fas fa-heartbeat"></i>     <!-- Health -->
<i class="fas fa-graduation-cap"></i> <!-- Education -->
<i class="fas fa-seedling"></i>      <!-- Agriculture -->
```

### Color Conventions
- **Primary**: `text-primary-600`
- **Success**: `text-green-600`  
- **Warning**: `text-yellow-600`
- **Error**: `text-red-600`
- **Info**: `text-blue-600`

## Color System

The platform uses a green-based color system with WCAG AA accessibility compliance.

### Primary Colors
```css
--color-primary-500: #22c55e;  /* Core brand green */
--color-primary-600: #16a34a;  /* Primary buttons */
--color-primary-700: #15803d;  /* Hover states */
```

### Status Colors
```css
--color-success-600: #059669;  /* Success */
--color-warning-600: #ea580c;  /* Warning */
--color-error-600: #dc2626;    /* Error */
--color-info-600: #2563eb;     /* Info */
```

### Neutral Colors
```css
--color-slate-600: #475569;    /* Body text */
--color-slate-700: #334155;    /* Heading text */
--color-slate-300: #cbd5e1;    /* Borders */
```

## Development Best Practices

- Always use component library instead of custom HTML/CSS
- Test all changes in Docker environment before committing
- Use Font Awesome icons consistently
- Follow Django/PEP 8 standards
- Write tests for new functionality
- Document complex logic and decisions

## Production Deployment

### Automated Fork Sync Process
The production site at https://fahaniecares.ph is deployed from a **forked repository** that automatically syncs with this main repository.

**Deployment Workflow**:
1. Push changes to `main` branch in this repository
2. Fork automatically syncs from main repository
3. Production rebuild triggers automatically
4. Changes go live at https://fahaniecares.ph

**To Deploy Changes**:
```bash
git add -A
git commit -m "Your change description"
git push origin main
# Fork sync and production deployment happen automatically
```

**Important**: No manual deployment scripts needed - just push to main for immediate production deployment.

### Production Environment
- **Live Site**: https://fahaniecares.ph
- **CDN**: CloudFront for static file caching
- **Container**: Docker production build via Coolify
- **Database**: PostgreSQL with Redis caching

## Known Issues & Fixes

### Radio Button State Preservation (Fixed ✅)
**Issue**: Radio buttons reset when registration form has validation errors, forcing users to re-select all options.

**Solution Implemented**:
1. **Template Dual State Checking**: 
   ```django
   {% if choice.is_checked or form.sex.value == choice.choice_value %}checked{% endif %}
   ```
   - Uses both Django's `choice.is_checked` AND form POST data `form.field.value`
   - Ensures radio buttons stay selected on validation errors

2. **JavaScript SessionStorage Backup**:
   ```javascript
   sessionStorage.setItem(`radio_${groupName}`, radio.value);
   ```
   - Client-side backup preserves selections even if template fails
   - Automatically restores selections on page reload

3. **Enhanced Form Handling**:
   - Modified `form_invalid()` method in `member_views.py:78`
   - Clear user messaging: "Your selections have been preserved"
   - Better debugging and error logging

**Files Modified**:
- `src/apps/constituents/templates/constituents/member_registration.html:154,268,293,329` (radio button templates)
- `src/apps/constituents/member_views.py:78` (form_invalid method)
- Added JavaScript state preservation logic lines 1085-1147

**Status**: ✅ Deployed to production, radio buttons now preserve state on form errors.

## Key Access Points

- **Development**: http://localhost:3000 (Docker)
- **Production**: https://fahaniecares.ph
- **Admin**: http://localhost:3000/admin (dev) / https://fahaniecares.ph/admin (prod)
- **Git Attribution**: "#FahanieCares Development Team"
- **Environment**: PostgreSQL + Redis + Django + TailwindCSS

