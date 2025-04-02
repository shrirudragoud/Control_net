@echo off
setlocal enabledelayedexpansion

echo Starting Virtual Try-On System setup...

:: Check Python version
python -c "import sys; ver = sys.version_info; exit(0 if ver.major >= 3 and ver.minor >= 8 else 1)"
if errorlevel 1 (
    echo Error: Python 3.8 or higher is required
    exit /b 1
)

:: Create directories
echo Creating necessary directories...
for %%d in (uploads "static/css" "static/js" templates models utils) do (
    if not exist "%%d" (
        mkdir "%%d"
        echo Created directory: %%d
    )
)

:: Check disk space (Windows PowerShell required)
echo Checking disk space...
powershell -Command "$drive = Get-PSDrive (Get-Location).Drive.Name; if ($drive.Free/1GB -lt 5) { exit 1 }"
if errorlevel 1 (
    echo Error: Insufficient disk space. At least 5GB required.
    exit /b 1
)

:: Setup virtual environment
if not exist "venv" (
    echo Creating virtual environment...
    python -m venv venv
)

:: Activate virtual environment
echo Activating virtual environment...
call venv\Scripts\activate.bat

:: Upgrade pip
echo Upgrading pip...
python -m pip install --upgrade pip

:: Install requirements
echo Installing requirements...
pip install -r requirements.txt

:: Check CUDA availability
echo Checking CUDA availability...
python -c "import torch; print(f'CUDA available: {torch.cuda.is_available()}')"
if errorlevel 1 (
    echo Warning: CUDA check failed. The application may run slower on CPU.
)

:: Download models
echo Checking and downloading required models...
python download_models.py
if errorlevel 1 (
    echo Error: Failed to download required models
    exit /b 1
)

:: Set default port if not specified
if "%PORT%"=="" (
    set PORT=5000
    echo Using default port: %PORT%
) else (
    echo Using custom port: %PORT%
)

:: Start Flask application
echo Starting Flask application...
python app.py

:: Deactivate virtual environment on exit
deactivate