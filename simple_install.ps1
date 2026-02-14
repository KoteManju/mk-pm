# Simple installation script for Project Management System
Write-Host "Installing Python and dependencies..." -ForegroundColor Green

# Try to install Python via winget if available
try {
    winget install Python.Python.3.11 --accept-package-agreements --accept-source-agreements --silent
    Write-Host "Python installed via winget" -ForegroundColor Green
} catch {
    Write-Host "Winget installation failed, downloading Python directly..." -ForegroundColor Yellow
    
    # Download Python installer
    $url = "https://www.python.org/ftp/python/3.11.8/python-3.11.8-amd64.exe"
    $output = "$env:TEMP\python-installer.exe"
    
    Invoke-WebRequest -Uri $url -OutFile $output
    Start-Process -FilePath $output -ArgumentList "/quiet InstallAllUsers=1 PrependPath=1" -Wait
    Remove-Item $output
}

# Refresh PATH
$env:Path = [System.Environment]::GetEnvironmentVariable("Path","Machine") + ";" + [System.Environment]::GetEnvironmentVariable("Path","User")

Write-Host "Installation complete. Please restart your terminal and run the test scripts." -ForegroundColor Green