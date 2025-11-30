@echo off
REM EduMentor AI Setup Script for Windows

echo ====================================
echo   EduMentor AI Setup
echo ====================================
echo.

REM Check Python
echo Checking Python installation...
python --version
if errorlevel 1 (
    echo ERROR: Python is not installed or not in PATH
    pause
    exit /b 1
)
echo.

REM Create virtual environment
echo Creating virtual environment...
python -m venv venv
echo.

REM Activate virtual environment
echo Activating virtual environment...
call venv\Scripts\activate.bat
echo.

REM Upgrade pip
echo Upgrading pip...
python -m pip install --upgrade pip
echo.

REM Install dependencies
echo Installing dependencies...
pip install -r requirements.txt
echo.

REM Create directories
echo Creating data directories...
if not exist "data\progress" mkdir data\progress
if not exist "data\memory" mkdir data\memory
if not exist "logs" mkdir logs
if not exist "logs\traces" mkdir logs\traces
echo.

REM Create .env file
if not exist ".env" (
    echo Creating .env file...
    copy .env.example .env
    echo.
    echo WARNING: Please edit .env and add your GOOGLE_API_KEY
    echo.
) else (
    echo .env file already exists
    echo.
)

REM Create __init__.py files
echo Creating Python package files...
type nul > agents\__init__.py
type nul > tools\__init__.py
type nul > config\__init__.py
echo.

echo ====================================
echo   Setup Complete!
echo ====================================
echo.
echo Next steps:
echo 1. Edit .env and add your GOOGLE_API_KEY
echo 2. Activate virtual environment: venv\Scripts\activate
echo 3. Run the application: python main.py
echo.
echo Happy learning!
echo.
pause