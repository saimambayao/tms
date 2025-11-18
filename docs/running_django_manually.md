# How to Run Django Server Manually

## Navigate to Project Root

```bash
cd /Users/macbookpro/Documents/fahanie-cares
```

## Method 1: Using Docker (Recommended)

```bash
# Start all services
docker-compose up -d

# Access the application at http://localhost:3000
```

## Method 2: Manual Setup

### 1. Navigate to src directory:

```bash
cd src
```

### 2. Create and activate virtual environment:

```bash
# Create virtual environment (first time only)
python3 -m venv venv

# Activate virtual environment
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

### 3. Install dependencies:

```bash
pip3 install -r requirements.txt
```

### 4. Install frontend dependencies:

```bash
# Install Node.js dependencies
npm install

# Build TailwindCSS
npm run build-css
```

### 5. Set up PostgreSQL database:

```bash
# Ensure PostgreSQL is running locally
# Create database and user
createdb fahaniecares_db
createuser fahaniecares_user

# Set environment variables
export DB_HOST=localhost
export DB_NAME=fahaniecares_db
export DB_USER=fahaniecares_user
export DB_PASSWORD=changeme
```

### 6. Run migrations:

```bash
python3 manage.py migrate
```

### 7. Collect static files:

```bash
python3 manage.py collectstatic --noinput
```

### 8. Create a superuser account (optional):

```bash
python3 manage.py createsuperuser
```

### 9. Run the development server:

```bash
# Default port (8000)
python3 manage.py runserver

# Custom port (3000) - matches Docker setup
python3 manage.py runserver 0.0.0.0:3000
```

## Access the Application

- Development server: http://localhost:3000
- Admin interface: http://localhost:3000/admin/

## Environment Variables

Create a `.env` file in the src directory with:

```env
# Django settings
DJANGO_SETTINGS_MODULE=config.settings.development
DEBUG=True
SECRET_KEY=your-secret-key-here

# Database settings
DB_ENGINE=django.db.backends.postgresql
DB_NAME=fahaniecares_db
DB_USER=fahaniecares_user
DB_PASSWORD=changeme
DB_HOST=localhost
DB_PORT=5432

# Redis (optional for local development)
REDIS_URL=redis://localhost:6379/0
```

## Notes

- PostgreSQL is now required (SQLite has been removed)
- The project root is `/Users/macbookpro/Documents/fahanie-cares`
- The Django source code is in the `src/` directory
- Static files are served from `src/staticfiles/` after running collectstatic
- Media files are stored in `src/media/`
- Always use `python3` and `pip3` to ensure Python 3 compatibility