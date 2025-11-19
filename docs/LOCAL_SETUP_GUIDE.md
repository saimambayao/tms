# Local Development Setup Guide (Without Docker)

This guide provides instructions on how to set up and run the Fahanie Cares application on your local machine without using Docker.

## 1. Prerequisites

Before you begin, ensure you have the following software installed on your system:

*   **Python:** Version 3.11.6. You can download it from the [official Python website](https://www.python.org/downloads/release/python-3116/).
*   **PostgreSQL:** Version 15 or later. Download it from the [official PostgreSQL website](https://www.postgresql.org/download/).
*   **Redis:** Version 7 or later. You can find installation instructions on the [official Redis website](https://redis.io/docs/getting-started/installation/).
*   **Node.js and npm:** Required for frontend asset management. Download and install the LTS version from the [official Node.js website](https://nodejs.org/). After installation, open a new terminal and run `npm -v` to verify that it is installed correctly.

## 2. Database Setup

1.  **Start PostgreSQL:** Ensure your PostgreSQL server is running.
2.  **Create Database and User:** You need to create a database and a user for the application. You can do this using the `psql` command-line tool or a graphical tool like pgAdmin.

    ```sql
    CREATE DATABASE fahaniecares_db;
    CREATE USER fahaniecares_user WITH PASSWORD 'changeme';
    ALTER ROLE fahaniecares_user SET client_encoding TO 'utf8';
    ALTER ROLE fahaniecares_user SET default_transaction_isolation TO 'read committed';
    ALTER ROLE fahaniecares_user SET timezone TO 'UTC';
    GRANT ALL PRIVILEGES ON DATABASE fahaniecares_db TO fahaniecares_user;
    ```

## 3. Environment Configuration

1.  **Create a `.env` file:** In the root of the project, create a file named `.env`. You can copy the contents from `.env.example` as a starting point.

2.  **Configure Environment Variables:** Open the `.env` file and set the following variables to match your local setup.

    ```ini
    # Django settings
    DJANGO_SETTINGS_MODULE=config.settings.development
    DEBUG=True
    SECRET_KEY=your-super-secret-key-that-is-long-and-random
    ALLOWED_HOSTS=localhost,127.0.0.1

    # Database settings
    DB_ENGINE=django.db.backends.postgresql
    DB_NAME=fahaniecares_db
    DB_USER=fahaniecares_user
    DB_PASSWORD=changeme
    DB_HOST=localhost
    DB_PORT=5432

    # Redis settings
    REDIS_URL=redis://localhost:6379/0
    CACHE_BACKEND=django_redis.cache.RedisCache

    # Email settings (development)
    EMAIL_BACKEND=django.core.mail.backends.console.EmailBackend
    ```

## 4. Backend Setup

1.  **Navigate to the `src` directory:**
    ```bash
    cd src
    ```

2.  **Create and Activate a Virtual Environment:**
    ```bash
    python -m venv venv
    # On Windows
    venv\Scripts\activate
    # On macOS/Linux
    source venv/bin/activate
    ```

3.  **Install Python Dependencies:**
    ```bash
    pip install -r requirements.txt
    ```

4.  **Run Database Migrations:**
    ```bash
    python manage.py migrate
    ```

## 5. Frontend Setup

1.  **Navigate to the `src` directory (if not already there):**
    ```bash
    cd src
    ```

2.  **Install Node.js Dependencies:**
    ```bash
    npm install
    ```

3.  **Build CSS files:**
    ```bash
    npm run build-css
    ```

## 6. Running the Application

You will need to run the Django development server and the Celery worker in separate terminals.

1.  **Start the Django Development Server:**
    *   Make sure you are in the `src` directory with your virtual environment activated.
    *   Run the following command:
        ```bash
        python manage.py runserver 0.0.0.0:3000
        ```
    *   The application should now be accessible at `http://localhost:3000`.

2.  **Start the Celery Worker:**
    *   Open a new terminal and navigate to the `src` directory.
    *   Activate the virtual environment.
    *   Run the following command:
        ```bash
        celery -A config worker -l info
        ```

Your local development environment is now set up and running.
