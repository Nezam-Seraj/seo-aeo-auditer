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
    echo  After installing Python, close this window and run SETUP.bat again.
    echo.
    pause
    exit /b 1
)

for /f "tokens=2" %%v in ('python --version 2^>^&1') do echo  [OK] Python %%v found.
echo.

:: ---------------------------------------------------
:: 2. Create virtual environment
:: ---------------------------------------------------
if exist ".venv\Scripts\python.exe" (
    echo  [OK] Virtual environment already exists.
) else (
    echo  Removing any broken virtual environment...
    if exist ".venv" rmdir /s /q ".venv"
    echo  Creating virtual environment...
    python -m venv .venv
    if not exist ".venv\Scripts\python.exe" (
        color 0C
        echo.
        echo  [ERROR] Failed to create virtual environment.
        echo  Try running this command manually in a terminal:
        echo    python -m venv .venv
        echo.
        pause
        exit /b 1
    )
    echo  [OK] Virtual environment created.
)
echo.

:: ---------------------------------------------------
:: 3. Install dependencies
:: ---------------------------------------------------
echo  Installing dependencies (this may take 1-2 minutes)...
echo  Please wait...
echo.
.venv\Scripts\pip install -r requirements.txt
if %errorlevel% neq 0 (
    color 0C
    echo.
    echo  [ERROR] Some dependencies failed to install.
    echo  This is usually a network issue. Try:
    echo    1. Check your internet connection
    echo    2. Close this window and run SETUP.bat again
    echo.
    pause
    exit /b 1
)
echo.
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
:: 6. Create Desktop Shortcut
:: ---------------------------------------------------
set "SHORTCUT=%USERPROFILE%\Desktop\SEO-AEO Analyzer.lnk"
if not exist "%SHORTCUT%" (
    echo  Creating desktop shortcut...
    powershell -Command "$ws = New-Object -ComObject WScript.Shell; $s = $ws.CreateShortcut('%SHORTCUT%'); $s.TargetPath = '%CD%\START_APP.bat'; $s.WorkingDirectory = '%CD%'; $s.Description = 'Launch SEO/AEO Analyzer'; $s.Save()"
    if exist "%SHORTCUT%" (
        echo  [OK] Desktop shortcut created: "SEO-AEO Analyzer"
    ) else (
        echo  [SKIP] Could not create shortcut — just double-click START_APP.bat instead.
    )
) else (
    echo  [OK] Desktop shortcut already exists.
)

:: ---------------------------------------------------
:: Done
:: ---------------------------------------------------
echo.
echo  ===================================================
echo    Setup Complete!
echo  ===================================================
echo.
echo  You can now launch the app by:
echo    - Double-clicking "SEO-AEO Analyzer" on your Desktop
echo    - Or double-clicking START_APP.bat in this folder
echo.
pause
