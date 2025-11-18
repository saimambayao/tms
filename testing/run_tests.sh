#!/bin/bash

# #FahanieCares Website Test Runner Script

set -e

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

echo "============================================"
echo "#FahanieCares Website Test Suite"
echo "============================================"

# Check if we're in the right directory
if [ ! -f "manage.py" ]; then
    echo -e "${RED}Error: manage.py not found. Please run this script from the project root.${NC}"
    exit 1
fi

# Activate virtual environment
if [ -d "venv" ]; then
    source venv/bin/activate
else
    echo -e "${YELLOW}Warning: Virtual environment not found.${NC}"
fi

# Install test dependencies
echo -e "${YELLOW}Installing test dependencies...${NC}"
pip install coverage pytest pytest-django pytest-cov

# Run Django checks
echo -e "${YELLOW}Running Django system checks...${NC}"
python manage.py check

# Run migrations check
echo -e "${YELLOW}Checking for unapplied migrations...${NC}"
python manage.py showmigrations | grep '\[ \]' && echo -e "${RED}Error: Unapplied migrations found${NC}" && exit 1

# Create test database
echo -e "${YELLOW}Setting up test database...${NC}"
python manage.py migrate --run-syncdb

# Run linting (if flake8 is installed)
if command -v flake8 &> /dev/null; then
    echo -e "${YELLOW}Running code linting...${NC}"
    flake8 apps/ --max-line-length=120 --exclude=migrations
fi

# Run unit tests with coverage
echo -e "${YELLOW}Running unit tests with coverage...${NC}"
coverage run --source='apps' manage.py test apps -v 2

# Generate coverage report
echo -e "${YELLOW}Generating coverage report...${NC}"
coverage report -m
coverage html

# Run specific test categories
echo -e "${YELLOW}Running model tests...${NC}"
python manage.py test apps --pattern="test_models.py" -v 2

echo -e "${YELLOW}Running view tests...${NC}"
python manage.py test apps --pattern="test_views.py" -v 2

echo -e "${YELLOW}Running form tests...${NC}"
python manage.py test apps --pattern="test_forms.py" -v 2

# Run integration tests
echo -e "${YELLOW}Running integration tests...${NC}"
python manage.py test apps.tests.test_integration -v 2

# Run performance tests
echo -e "${YELLOW}Running performance tests...${NC}"
python manage.py test apps.tests.test_performance -v 2

# Check for security issues
echo -e "${YELLOW}Running security checks...${NC}"
python manage.py check --deploy

# Generate test report
echo -e "${YELLOW}Generating test report...${NC}"
echo "Test Report - $(date)" > test_report.txt
echo "================================" >> test_report.txt
coverage report >> test_report.txt

# Summary
echo -e "${GREEN}============================================${NC}"
echo -e "${GREEN}Test suite completed successfully!${NC}"
echo -e "${GREEN}Coverage report: htmlcov/index.html${NC}"
echo -e "${GREEN}Test report: test_report.txt${NC}"
echo -e "${GREEN}============================================${NC}"