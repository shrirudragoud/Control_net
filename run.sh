#!/bin/bash

# Exit on any error
set -e

echo "Starting Virtual Try-On System setup..."

# Create necessary directories
echo "Creating directories..."
mkdir -p uploads
mkdir -p static/css
mkdir -p static/js
mkdir -p templates
mkdir -p utils

# Set correct permissions
echo "Setting permissions..."
chmod -R 755 uploads
chmod -R 755 static
chmod -R 755 templates
chmod -R 755 utils

# Check if virtual environment exists
if [ ! -d "venv" ]; then
    echo "Creating virtual environment..."
    python -m venv venv
fi

# Activate virtual environment
echo "Activating virtual environment..."
source venv/bin/activate

# Install requirements
echo "Installing requirements..."
pip install -r requirements.txt

# Ensure the SAM model exists
if [ ! -f "sam_vit_h_4b8939.pth" ]; then
    echo "WARNING: SAM model checkpoint not found!"
    echo "Downloading SAM model checkpoint..."
    wget https://dl.fbaipublicfiles.com/segment_anything/sam_vit_h_4b8939.pth
fi

# Check if port is provided as an environment variable
if [ -z "${PORT}" ]; then
    echo "No PORT environment variable found, defaulting to 5000"
    export PORT=5000
fi

echo "Starting Flask application on port ${PORT}..."
# Start the Flask application
python app.py