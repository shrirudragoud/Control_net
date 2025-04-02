#!/bin/bash

# Exit on any error
set -e

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# Function to print error message and exit
error_exit() {
    echo -e "${RED}Error: $1${NC}" >&2
    exit 1
}

# Function to print success message
success_msg() {
    echo -e "${GREEN}$1${NC}"
}

# Function to print warning message
warning_msg() {
    echo -e "${YELLOW}$1${NC}"
}

# Check if Python is installed
if ! command -v python3 &> /dev/null; then
    error_exit "Python is not installed. Please install Python 3.8 or higher."
fi

# Check Python version
python_version=$(python3 -c 'import sys; print(".".join(map(str, sys.version_info[:2])))')
if (( $(echo "$python_version < 3.8" | bc -l) )); then
    error_exit "Python 3.8 or higher is required. Found version: $python_version"
fi

# Create and activate virtual environment
if [ ! -d "venv" ]; then
    echo "Creating virtual environment..."
    python3 -m venv venv || error_exit "Failed to create virtual environment"
fi

# Activate virtual environment
echo "Activating virtual environment..."
source venv/bin/activate || error_exit "Failed to activate virtual environment"

# Run the setup and check script
echo "Running system checks and setup..."
python check_and_setup.py || error_exit "Setup failed. Please check the errors above."

# Start the application
success_msg "\nSetup completed successfully!"
echo "Starting the application..."
warning_msg "The web interface will be available at http://localhost:5000"
echo "Press Ctrl+C to stop the application"
echo

# Start the Flask application
python app.py

# Deactivate virtual environment on exit
deactivate