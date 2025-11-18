# Set the execution policy for the current process to allow scripts to run
Set-ExecutionPolicy -ExecutionPolicy Unrestricted -Scope Process

# Set location to the src directory
Set-Location -Path "src"

# Set the local python version
pyenv local 3.11.6

# Create a virtual environment if it doesn't exist
if (-not (Test-Path "venv")) {
    python -m venv venv
}

# Activate the virtual environment
. .\venv\Scripts\Activate.ps1

# Upgrade pip
python.exe -m pip install --upgrade pip

# Install Python dependencies
pip install -r requirements.txt

# Check if npm is installed
if (-not (Get-Command "npm" -ErrorAction SilentlyContinue)) {
    Write-Host "Node.js and npm are not installed or not in your PATH. Please install them to continue."
    exit 1
}

# Install Node.js dependencies
npm install

# Build CSS
npm run build-css

# Run database migrations
python manage.py migrate

# Start the Django development server
python manage.py runserver localhost:3000
