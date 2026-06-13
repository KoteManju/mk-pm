@echo off
echo Stopping backend Python processes on port 8000...
for /f "tokens=5" %%a in ('netstat -aon ^| findstr :8000 ^| findstr LISTENING') do taskkill /f /pid %%a >nul 2>&1
timeout /t 2 /nobreak >nul

echo Recreating database...
cd /d "%~dp0backend"
set "PYTHONPATH=%~dp0backend"

python --version >nul 2>&1
if %errorlevel% neq 0 (
    set "PYTHON_PATH=%LOCALAPPDATA%\Programs\Python\Python311"
    if exist "%PYTHON_PATH%\python.exe" (
        set "PATH=%PYTHON_PATH%;%PYTHON_PATH%\Scripts;%PATH%"
    )
)

del project_management.db >nul 2>&1
python init_db.py

echo Starting backend server...
python -m uvicorn main:app --host 127.0.0.1 --port 8000 --reload

pause
