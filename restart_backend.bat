@echo off
echo Stopping all Python processes...
taskkill /f /im python.exe >nul 2>&1
timeout /t 2 /nobreak >nul

echo Recreating database...
cd /d "C:\Users\Mkotegar\Documents\mk\TGS\PM\backend"
del project_management.db >nul 2>&1
"C:\Users\Mkotegar\AppData\Local\Programs\Python\Python311\python.exe" init_db.py

echo Starting backend server...
set PYTHONPATH=C:\Users\Mkotegar\Documents\mk\TGS\PM\backend
"C:\Users\Mkotegar\AppData\Local\Programs\Python\Python311\python.exe" -m uvicorn main:app --host 127.0.0.1 --port 8000 --reload

pause