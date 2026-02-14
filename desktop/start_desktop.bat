@echo off
cd /d "%~dp0"
echo Starting Project Management Desktop App...
echo.

REM Refresh PATH environment  
call refreshenv >nul 2>&1

REM Try to find Python
python --version >nul 2>&1
if %errorlevel% neq 0 (
    echo Python not found in PATH. Trying alternative...
    set "PYTHON_PATH=%LOCALAPPDATA%\Programs\Python\Python311"
    if exist "%PYTHON_PATH%\python.exe" (
        set "PATH=%PYTHON_PATH%;%PYTHON_PATH%\Scripts;%PATH%"
    )
)

echo Starting desktop application...
python main.py

pause