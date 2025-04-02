#!/bin/bash

# Exit on any error
set -e

echo "Starting Virtual Try-On System setup..."

# Function to check Python version
check_python_version() {
    required_version="3.8"
    python_version=$(python -c 'import sys; print(".".join(map(str, sys.version_info[:2])))')
    
    if [ "$(printf '%s\n' "$required_version" "$python_version" | sort -V | head -n1)" != "$required_version" ]; then
        echo "Error: Python version $required_version or higher is required"
        echo "Current version: $python_version"
        exit 1
    fi
}

# Function to check CUDA availability
check_cuda() {
    echo "Checking CUDA availability..."
    python -c "import torch; print(f'CUDA available: {torch.cuda.is_available()}')"
    if [ $? -ne 0 ]; then
        echo "Warning: CUDA check failed. The application may run slower on CPU."
    fi
}

# Function to create directories
create_directories() {
    echo "Creating necessary directories..."
    directories=("uploads" "static/css" "static/js" "templates" "models" "utils")
    for dir in "${directories[@]}"; do
        mkdir -p "$dir"
        echo "Created directory: $dir"
    done
}

# Function to check disk space
check_disk_space() {
    required_gb=5
    available_gb=$(df -BG . | awk 'NR==2 {print $4}' | sed 's/G//')
    
    if [ "$available_gb" -lt "$required_gb" ]; then
        echo "Error: Insufficient disk space"
        echo "Required: ${required_gb}GB"
        echo "Available: ${available_gb}GB"
        exit 1
    fi
}

# Function to setup virtual environment
setup_venv() {
    if [ ! -d "venv" ]; then
        echo "Creating virtual environment..."
        python -m venv venv
    fi
    
    echo "Activating virtual environment..."
    source venv/bin/activate || source venv/Scripts/activate
    
    echo "Upgrading pip..."
    python -m pip install --upgrade pip
    
    echo "Installing requirements..."
    pip install -r requirements.txt
}

# Function to download models
download_models() {
    echo "Checking and downloading required models..."
    python download_models.py
    if [ $? -ne 0 ]; then
        echo "Error: Failed to download required models"
        exit 1
    fi
}

# Main execution
main() {
    echo "Checking system requirements..."
    check_python_version
    check_disk_space
    
    create_directories
    setup_venv
    check_cuda
    download_models
    
    echo "Starting Flask application..."
    if [ -n "$PORT" ]; then
        echo "Using custom port: $PORT"
    else
        export PORT=5000
        echo "Using default port: $PORT"
    fi
    
    python app.py
}

# Error handling
handle_error() {
    echo "Error occurred at line $1"
    exit 1
}

trap 'handle_error $LINENO' ERR

# Run main function
main