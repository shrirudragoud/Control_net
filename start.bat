@echo off
setlocal enabledelayedexpansion
title Virtual Try-On System Setup

:: Check if Python is installed
python --version >nul 2>&1
if errorlevel 1 (
    echo Error: Python is not installed or not in PATH
    echo Please install Python 3.8 or higher from python.org
    pause
    exit /b 1
)

:: Create and activate virtual environment
if not exist "venv" (
    echo Creating virtual environment...
    python -m venv venv
)

:: Activate virtual environment
call venv\Scripts\activate.bat

:: Run the setup and check script
echo Running system checks and setup...
python check_and_setup.py
if errorlevel 1 (
    echo.
    echo Setup failed. Please check the errors above.
    pause
    exit /b 1
)

:: Start the application
echo.
echo Starting the application...
echo The web interface will be available at http://localhost:5000
echo.
echo Press Ctrl+C to stop the application
echo.
python app.py

:: Deactivate virtual environment on exit
deactivate

pause