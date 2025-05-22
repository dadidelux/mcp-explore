# Kill any existing processes on ports 3000 and 8000
try {
    Get-Process -Id (Get-NetTCPConnection -LocalPort 3000).OwningProcess -ErrorAction SilentlyContinue | Stop-Process -Force
    Get-Process -Id (Get-NetTCPConnection -LocalPort 8000).OwningProcess -ErrorAction SilentlyContinue | Stop-Process -Force
} catch {
    Write-Host "No existing processes to stop"
}

# Set environment variables
$env:PYTHONPATH = $PSScriptRoot
$env:DJANGO_DEBUG = "True"

# Start Django backend in a new window
Start-Process powershell -ArgumentList "-NoExit", "-Command", "Set-Location '$PSScriptRoot\src\django_app'; python manage.py runserver"

# Start React frontend in a new window
Start-Process powershell -ArgumentList "-NoExit", "-Command", "Set-Location '$PSScriptRoot\src\react-frontend'; npm start"

Write-Host "Development servers started:"
Write-Host "Django backend: http://localhost:8000"
Write-Host "React frontend: http://localhost:3000"
Write-Host "Press Ctrl+C in the respective windows to stop the servers"
