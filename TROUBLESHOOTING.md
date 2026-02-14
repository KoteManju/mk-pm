# Project Management System - Troubleshooting Guide

## Current Issue: Login Failures

### Symptoms
- Desktop app: "Invalid username or password"
- Swagger UI: Internal Server Error when creating users
- Backend is running on http://127.0.0.1:8000

### Root Cause
The backend is running, but there may be:
1. Password hash mismatch in database
2. Backend not receiving requests properly
3. Database not initialized properly

### Solution Steps

#### Step 1: Verify Backend is Accessible
Open PowerShell and run:
```powershell
curl.exe http://127.0.0.1:8000/docs
```
If this works, backend is running ✅

#### Step 2: Test Login Directly
```powershell
cd C:\Users\Mkotegar\Documents\mk\TGS\PM\backend
python test_auth.py
```

This will test:
- Login with admin/admin123
- User creation

#### Step 3: Check Database
```powershell
cd C:\Users\Mkotegar\Documents\mk\TGS\PM\backend  
python check_db.py
```

Should show:
```
Tables: ['users', 'projects', 'tasks']

Users:
  ID: 1, Username: admin, Email: admin@example.com
  ID: 2, Username: user, Email: user@example.com

Projects:
  ID: 1, Name: Sample Project, Owner ID: 1
```

#### Step 4: If Database is Empty or Corrupted
```powershell
cd C:\Users\Mkotegar\Documents\mk\TGS\PM\backend

# Delete old database
del project_management.db

# Create fresh database
python init_db.py
```

Expected output:
```
🗄️ Initializing database...
📝 Creating sample data...
✅ Database initialized successfully!

📋 Sample data created:
   Users: admin/admin123, user/user123
   Project: Sample Project
   Tasks: 4 sample tasks
```

#### Step 5: Restart Everything
1. **Stop backend**: Press Ctrl+C in the backend terminal
2. **Start backend**: Run `start_backend.bat`
3. **Wait** for "Application startup complete"
4. **Close desktop app** if running
5. **Start desktop**: Run `start_desktop.bat`
6. **Login** with admin/admin123

### Test Login from Desktop App

1. Open desktop app
2. Enter:
   - Username: `admin`
   - Password: `admin123`
3. Click Login

### If Still Failing

Run the health check:
```powershell
cd C:\Users\Mkotegar\Documents\mk\TGS\PM
python health_check.py
```

This will show exactly what's working and what's not.

### Expected Working State

**Backend Terminal Shows:**
```
INFO:     Uvicorn running on http://127.0.0.1:8000 (Press CTRL+C to quit)
INFO:     Started server process [XXXXX]
INFO:     Waiting for application startup.
INFO:     Application startup complete.
```

**When you login, you should see:**
```
INFO:     127.0.0.1:XXXXX - "POST /api/auth/token HTTP/1.1" 200 OK
```

**Desktop App Console Shows:**
```
Attempting login for user: admin
API URL: http://localhost:8000/api/auth/token
Response status code: 200
Login successful, token: eyJhbGciOiJIUzI1NiIsInR5...
```

### Quick Commands Reference

**Check if port 8000 is in use:**
```powershell
netstat -ano | findstr :8000
```

**Kill all Python processes:**
```powershell
taskkill /f /im python.exe
```

**Test API endpoint directly:**
```powershell
# Login
curl.exe -X POST "http://127.0.0.1:8000/api/auth/token" -H "Content-Type: application/x-www-form-urlencoded" -d "username=admin&password=admin123"

# Create task
curl.exe -X POST "http://127.0.0.1:8000/api/tasks/" -H "Content-Type: application/json" -d "{\"title\": \"Test\", \"status\": \"todo\", \"priority\": \"medium\"}"
```

---
**Quick Fix Script**

Save this as `quick_fix.bat`:
```batch
@echo off
echo Resetting Project Management System...
taskkill /f /im python.exe >nul 2>&1
cd backend
del project_management.db
python init_db.py
cd ..
echo.
echo Done! Now run:
echo 1. start_backend.bat
echo 2. start_desktop.bat
pause
```
