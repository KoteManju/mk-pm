@echo off
echo ========================================
echo Starting Project Management Backend
echo ========================================
echo.

cd /d "%~dp0backend"
set "PYTHONPATH=%~dp0backend"

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

if not exist project_management.db (
    echo Initializing database...
    python init_db.py
    echo.
) else (
    echo Applying database updates...
    python migrate_chat_features.py >nul 2>&1
    python migrate_email_features.py >nul 2>&1
    python migrate_attachments.py >nul 2>&1
)

echo Starting FastAPI server on http://127.0.0.1:8000
echo API Documentation: http://127.0.0.1:8000/docs
echo.

for /f "tokens=5" %%a in ('netstat -aon ^| findstr :8000 ^| findstr LISTENING') do (
    echo WARNING: Port 8000 is already in use. Stopping process PID %%a ...
    taskkill /f /pid %%a >nul 2>&1
)
for /f "tokens=2" %%a in ('wmic process where "CommandLine like '%%uvicorn%%main:app%%'" get ProcessId /format:value ^| findstr ProcessId') do (
    echo Stopping leftover uvicorn process PID %%a ...
    taskkill /f /pid %%a >nul 2>&1
)
timeout /t 2 /nobreak >nul

echo.
echo Backend version check after start - open http://127.0.0.1:8000/health
echo Expected: attachments_enabled=true, version=1.1.0
echo.

python -m uvicorn main:app --host 127.0.0.1 --port 8000

pause
