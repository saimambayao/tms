# Set the execution policy for the current process to allow scripts to run
Set-ExecutionPolicy -ExecutionPolicy Unrestricted -Scope Process

# Set location to the src directory
Set-Location -Path "src"

# Activate the virtual environment
. .\venv\Scripts\Activate.ps1

# Run database migrations
python manage.py migrate
