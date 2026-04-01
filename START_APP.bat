@echo off
title SEO/AEO Analyzer
color 0B

:: ---------------------------------------------------
:: Quick checks
:: ---------------------------------------------------
if not exist ".venv" (
    color 0E
    echo.
    echo  Virtual environment not found. Running setup first...
    echo.
    call SETUP.bat
    if %errorlevel% neq 0 exit /b 1
)

if not exist ".env" (
    color 0E
    echo.
    echo  API keys not configured. Running setup first...
    echo.
    call SETUP.bat
    if %errorlevel% neq 0 exit /b 1
)

:: ---------------------------------------------------
:: Launch the app
:: ---------------------------------------------------
color 0A
echo.
echo  ===================================================
echo    Launching SEO/AEO Analyzer...
echo  ===================================================
echo.
echo  The app will open in your browser automatically.
echo  If it doesn't, go to: http://localhost:8501
echo.
echo  To stop the app, close this window.
echo  ===================================================
echo.

.venv\Scripts\streamlit run app.py
