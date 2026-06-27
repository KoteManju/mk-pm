@echo off
echo ========================================
echo Starting Project Management Desktop App
echo ========================================
echo.

cd /d "%~dp0desktop"

REM Try to find Python
python --version >nul 2>&1
if %errorlevel% neq 0 (
    echo Python not found in PATH. Trying alternative...
    set "PYTHON_PATH=%LOCALAPPDATA%\Programs\Python\Python311"
    if exist "%PYTHON_PATH%\python.exe" (
        set "PATH=%PYTHON_PATH%;%PYTHON_PATH%\Scripts;%PATH%"
    ) else (
        echo ERROR: Python is not installed.
        echo Run install_dependencies.ps1 first, then try again.
        pause
        exit /b 1
    )
)

echo.
echo Connects to the API URL in desktop\settings.json
echo (default cloud server or http://127.0.0.1:8000 for local dev).
echo Change it in the app under Settings if needed.
echo.
echo Login Credentials:
echo   Username: admin
echo   Password: admin123
echo.
echo   OR
echo.
echo   Username: user
echo   Password: user123
echo.
echo Starting application...
echo.

python main.py

pause
