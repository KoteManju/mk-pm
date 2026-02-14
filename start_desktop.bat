@echo off
echo ========================================
echo Starting Project Management Desktop App
echo ========================================
echo.

cd /d "%~dp0desktop"

echo.
echo Make sure the backend is running on http://127.0.0.1:8000
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

"C:\Users\Mkotegar\AppData\Local\Programs\Python\Python311\python.exe" main.py

pause
