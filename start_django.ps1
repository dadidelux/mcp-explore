try {
    # Try to stop any existing process on port 8000
    Stop-Process -Id (Get-NetTCPConnection -LocalPort 8000).OwningProcess -Force -ErrorAction SilentlyContinue
} catch {
    Write-Host "No existing process to stop on port 8000"
}

# Set environment variables and Python path
$env:PYTHONPATH = "c:\Users\dadidelux\Documents\Programs\mcp_explore"
$env:DJANGO_DEBUG = "True"

# Change directory and start Django server
Set-Location -Path "c:\Users\dadidelux\Documents\Programs\mcp_explore\src\django_app"
python manage.py runserver
