#!/bin/bash

# Define the absolute path to the Django project directory
DJANGO_PROJECT_PATH="c:/Users/User/Desktop/fahanie-cares/src"

# Navigate to the Django project directory
cd "$DJANGO_PROJECT_PATH"

# Start the Django development server in the background
python manage.py runserver &

# Get the process ID of the last background command
DJANGO_PID=$!

# Wait a few seconds for the server to start
sleep 5

# Wait for the Django server process to finish (or for user to manually stop it)
wait $DJANGO_PID
