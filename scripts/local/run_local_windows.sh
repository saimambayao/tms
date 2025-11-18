#!/bin/bash

# Define the absolute path to the Django project directory
DJANGO_PROJECT_PATH="d:/fahanie-cares/src"

# Navigate to the Django project directory
cd "$DJANGO_PROJECT_PATH"

# Start the Django development server in the background
python3 manage.py runserver &

# Get the process ID of the last background command
DJANGO_PID=$!

# Wait a few seconds for the server to start
sleep 5

# Open the project URL in the default browser for Windows
start http://127.0.0.1:8000/

# Wait for the Django server process to finish (or for user to manually stop it)
wait $DJANGO_PID
