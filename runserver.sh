#!/bin/bash

# BM Parliament - Local Development Server Runner
# This script runs the Django development server locally on port 3080

set -e  # Exit on error

# Colors for output
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
NC='\033[0m' # No Color

# Get the script directory (project root)
SCRIPT_DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"
SRC_DIR="${SCRIPT_DIR}/src"
PORT=3080

echo -e "${GREEN}========================================${NC}"
echo -e "${GREEN}BM Parliament - Local Development Server${NC}"
echo -e "${GREEN}========================================${NC}"
echo ""

# Check if src directory exists
if [ ! -d "$SRC_DIR" ]; then
    echo -e "${RED}Error: src directory not found at ${SRC_DIR}${NC}"
    exit 1
fi

# Navigate to src directory
cd "$SRC_DIR"
echo -e "${YELLOW}Working directory: $(pwd)${NC}"
echo ""

# Check if virtual environment exists
if [ -d "venv" ]; then
    echo -e "${GREEN}Activating virtual environment...${NC}"
    source venv/bin/activate
elif [ -d "../venv" ]; then
    echo -e "${GREEN}Activating virtual environment from parent directory...${NC}"
    source ../venv/bin/activate
else
    echo -e "${YELLOW}Warning: No virtual environment found. Using system Python.${NC}"
    echo -e "${YELLOW}Consider creating a virtual environment: python3 -m venv venv${NC}"
fi

echo ""

# Check if Python is available
if ! command -v python3 &> /dev/null; then
    echo -e "${RED}Error: python3 is not installed or not in PATH${NC}"
    exit 1
fi

# Check if Django is installed
if ! python3 -c "import django" 2>/dev/null; then
    echo -e "${RED}Error: Django is not installed${NC}"
    echo -e "${YELLOW}Please install dependencies: pip install -r requirements.txt${NC}"
    exit 1
fi

# Check if port is already in use
if lsof -Pi :$PORT -sTCP:LISTEN -t >/dev/null 2>&1 ; then
    echo -e "${YELLOW}Warning: Port $PORT is already in use${NC}"
    echo -e "${YELLOW}Attempting to stop existing server...${NC}"
    pkill -f "manage.py runserver.*$PORT" || true
    sleep 2
fi

echo -e "${GREEN}Starting Django development server on port $PORT...${NC}"
echo -e "${GREEN}Server will be available at: http://localhost:$PORT${NC}"
echo -e "${GREEN}Press Ctrl+C to stop the server${NC}"
echo ""

# Run the Django development server
python3 manage.py runserver 0.0.0.0:$PORT

