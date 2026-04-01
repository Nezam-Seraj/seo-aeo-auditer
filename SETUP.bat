@echo off
title SEO/AEO Analyzer - Setup
color 0A
echo.
echo  ===================================================
echo    SEO/AEO Analyzer - First-Time Setup
echo  ===================================================
echo.

:: ---------------------------------------------------
:: 1. Check for Python
:: ---------------------------------------------------
python --version >nul 2>&1
if %errorlevel% neq 0 (
    color 0C
    echo  [ERROR] Python is not installed or not in PATH.
    echo.
    echo  Please install Python 3.10+ from:
    echo  https://www.python.org/downloads/
    echo.
    echo  IMPORTANT: During installation, check the box that says
    echo  "Add Python to PATH"
    echo.
    pause
    exit /b 1
)

echo  [OK] Python found.
echo.

:: ---------------------------------------------------
:: 2. Create virtual environment
:: ---------------------------------------------------
if not exist ".venv" (
    echo  Creating virtual environment...
    python -m venv .venv
    echo  [OK] Virtual environment created.
) else (
    echo  [OK] Virtual environment already exists.
)
echo.

:: ---------------------------------------------------
:: 3. Install dependencies
:: ---------------------------------------------------
echo  Installing dependencies (this may take a minute)...
.venv\Scripts\pip install -r requirements.txt --quiet
echo  [OK] Dependencies installed.
echo.

:: ---------------------------------------------------
:: 4. Check for .env file
:: ---------------------------------------------------
if not exist ".env" (
    echo  ===================================================
    echo    API Key Setup
    echo  ===================================================
    echo.
    echo  You need two API keys to run this tool.
    echo.
    set /p GEMINI_KEY="  Enter your Gemini API Key: "
    set /p BING_KEY="  Enter your Bing Webmaster API Key (or press Enter to skip): "
    echo.
    (
        echo GEMINI_API_KEY=%GEMINI_KEY%
        echo BING_API_KEY=%BING_KEY%
    ) > .env
    echo  [OK] API keys saved to .env file.
) else (
    echo  [OK] API keys already configured (.env exists).
)
echo.

:: ---------------------------------------------------
:: 5. Check for credentials.json
:: ---------------------------------------------------
if not exist "credentials.json" (
    color 0E
    echo  ===================================================
    echo    IMPORTANT: Google Credentials Missing
    echo  ===================================================
    echo.
    echo  To use Client Mode (GSC, GA4, GBP data), you need
    echo  a "credentials.json" file in this folder.
    echo.
    echo  Ask Nezam for this file, or copy it from the
    echo  shared drive and drop it into:
    echo  %CD%
    echo.
    echo  You can still use Prospect/Competitor Mode without it.
    echo.
    color 0A
) else (
    echo  [OK] Google credentials found.
)

:: ---------------------------------------------------
:: Done
:: ---------------------------------------------------
echo.
echo  ===================================================
echo    Setup Complete!
echo  ===================================================
echo.
echo  To launch the app, double-click: START_APP.bat
echo.
pause
