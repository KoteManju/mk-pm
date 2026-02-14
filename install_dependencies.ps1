# PowerShell script to install Python and required packages
# Run this script to set up everything needed for the project

Write-Host "🐍 Installing Python and Dependencies for Project Management System" -ForegroundColor Green
Write-Host ""

# Function to check if Python is available
function Test-Python {
    try {
        $version = & python --version 2>&1
        if ($version -like "*Python*") {
            Write-Host "✅ Python found: $version" -ForegroundColor Green
            return $true
        }
    } catch {}
    return $false
}

# Function to install Python via winget (Windows Package Manager)
function Install-PythonWinget {
    Write-Host "📦 Installing Python via Windows Package Manager..."
    try {
        winget install Python.Python.3.11 --accept-package-agreements --accept-source-agreements
        return $true
    } catch {
        Write-Host "❌ Failed to install Python via winget" -ForegroundColor Red
        return $false
    }
}

# Function to download and install Python manually
function Install-PythonDirect {
    Write-Host "🌐 Downloading Python installer..."
    $url = "https://www.python.org/ftp/python/3.11.8/python-3.11.8-amd64.exe"
    $output = "$env:TEMP\python-installer.exe"
    
    try {
        Invoke-WebRequest -Uri $url -OutFile $output
        Write-Host "🔧 Installing Python..."
        Start-Process -FilePath $output -ArgumentList "/quiet InstallAllUsers=1 PrependPath=1 Include_test=0" -Wait
        Remove-Item $output -ErrorAction SilentlyContinue
        return $true
    } catch {
        Write-Host "❌ Failed to download or install Python" -ForegroundColor Red
        return $false
    }
}

# Function to refresh environment variables
function Update-Environment {
    Write-Host "🔄 Refreshing environment variables..."
    $env:Path = [System.Environment]::GetEnvironmentVariable("Path","Machine") + ";" + [System.Environment]::GetEnvironmentVariable("Path","User")
}

# Function to install backend dependencies
function Install-BackendDependencies {
    Write-Host "📦 Installing backend dependencies..."
    $packages = @(
        "fastapi",
        "uvicorn[standard]",
        "sqlalchemy",
        "pydantic[email]",
        "python-dotenv",
        "pydantic-settings",
        "python-jose[cryptography]",
        "passlib[bcrypt]",
        "python-multipart"
    )
    
    foreach ($package in $packages) {
        Write-Host "   Installing $package..."
        python -m pip install $package --quiet
    }
}

# Function to install desktop dependencies
function Install-DesktopDependencies {
    Write-Host "🖥️  Installing desktop app dependencies..."
    $packages = @(
        "PySide6",
        "requests"
    )
    
    foreach ($package in $packages) {
        Write-Host "   Installing $package..."
        python -m pip install $package --quiet
    }
}

# Main installation process
Write-Host "Checking for Python installation..." -ForegroundColor Yellow

if (Test-Python) {
    Write-Host "Python is already available!" -ForegroundColor Green
} else {
    Write-Host "Python not found. Installing..." -ForegroundColor Yellow
    
    # Try winget first
    if (Get-Command winget -ErrorAction SilentlyContinue) {
        if (Install-PythonWinget) {
            Update-Environment
            Start-Sleep -Seconds 5
        }
    }
    
    # If winget failed or not available, try direct download
    if (-not (Test-Python)) {
        Install-PythonDirect
        Update-Environment
        Start-Sleep -Seconds 5
    }
    
    # Final check
    if (-not (Test-Python)) {
        Write-Host "❌ Failed to install Python. Please install Python manually from https://python.org" -ForegroundColor Red
        exit 1
    }
}

# Install dependencies
try {
    Install-BackendDependencies
    Install-DesktopDependencies
    
    Write-Host ""
    Write-Host "✅ Installation complete!" -ForegroundColor Green
    Write-Host ""
    Write-Host "🚀 To start the backend:" -ForegroundColor Cyan
    Write-Host "   cd backend"
    Write-Host "   python -m uvicorn main:app --reload --host 0.0.0.0 --port 8000"
    Write-Host ""
    Write-Host "🖥️  To start the desktop app:" -ForegroundColor Cyan
    Write-Host "   cd desktop"
    Write-Host "   python main.py"
    Write-Host ""
    
} catch {
    Write-Host "❌ Error installing dependencies: $($_.Exception.Message)" -ForegroundColor Red
    exit 1
}