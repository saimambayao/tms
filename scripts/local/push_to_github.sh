#!/bin/bash

# Replace YOUR_GITHUB_USERNAME with your actual GitHub username
# Replace YOUR_REPOSITORY_NAME with the repository name you created

echo "Setting up GitHub remote..."
cd /Users/macbookpro/Documents/fahanie-cares

# Remove existing remote if any
git remote remove origin 2>/dev/null

# Add your GitHub repository as origin
# IMPORTANT: Replace the URL below with your actual GitHub repository URL
git remote add origin https://github.com/mpuyoyod/fahanie-cares.git

# Push to GitHub
echo "Pushing to GitHub..."
git push -u origin main

echo "Done! Your code is now on GitHub."