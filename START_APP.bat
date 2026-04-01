@echo off
title SEO/AEO Analyzer
color 0B

:: ---------------------------------------------------
:: Quick checks — run setup if needed
:: ---------------------------------------------------
if not exist ".venv\Scripts\streamlit.exe" (
    color 0E
    echo.
    echo  First-time setup needed. Running setup...
    echo.
    call SETUP.bat
    if %errorlevel% neq 0 (
        echo.
        echo  Setup failed. Please fix the errors above and try again.
        echo.
        pause
        exit /b 1
    )
)

if not exist ".env" (
    color 0E
    echo.
    echo  API keys not configured. Running setup...
    echo.
    call SETUP.bat
    if %errorlevel% neq 0 (
        echo.
        echo  Setup failed. Please fix the errors above and try again.
        echo.
        pause
        exit /b 1
    )
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

:: If we get here, streamlit exited (crashed or was closed)
echo.
echo  ===================================================
echo  The app has stopped.
echo  ===================================================
echo.
echo  If this was unexpected, try running START_APP.bat again.
echo  If the problem persists, delete the ".venv" folder
echo  and run SETUP.bat to reinstall.
echo.
pause
