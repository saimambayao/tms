# Set the execution policy for the current process to allow scripts to run
Set-ExecutionPolicy -ExecutionPolicy Unrestricted -Scope Process

# Activate the virtual environment
. .\venv\Scripts\Activate.ps1

# Set location to the src directory
Set-Location -Path "src"

# Start the Django development server using the full path to python.exe
.\venv\Scripts\python.exe manage.py runserver localhost:3000
