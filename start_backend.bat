@echo off
echo Stopping all Python processes...
taskkill /f /im python.exe >nul 2>&1
timeout /t 3 /nobreak >nul

echo Starting backend server...
cd /d "C:\Users\Mkotegar\Documents\mk\TGS\PM\backend"
set PYTHONPATH=C:\Users\Mkotegar\Documents\mk\TGS\PM\backend
"C:\Users\Mkotegar\AppData\Local\Programs\Python\Python311\python.exe" -m uvicorn main:app --host 127.0.0.1 --port 8000 --reload

pause