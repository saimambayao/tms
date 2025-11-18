#!/bin/bash
set -e

echo "🚀 Starting #FahanieCares Production Server"
echo "================================================"

# DEBUG: Print all environment variables to the log
echo "--- DUMPING ENVIRONMENT VARIABLES ---"
printenv
echo "-------------------------------------"

echo "🎉 #FahanieCares Production Server Ready!"
echo "================================================"

# Run deployment tasks
/app/run_deployment_tasks.sh

# Execute the main command (from Procfile)
exec "$@"
