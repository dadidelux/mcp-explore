try {
    # Try to stop any existing process on port 5000
    Stop-Process -Id (Get-NetTCPConnection -LocalPort 5000).OwningProcess -Force -ErrorAction SilentlyContinue
} catch {
    Write-Host "No existing process to stop on port 5000"
}

# Set environment variables and Python path
$env:PYTHONPATH = "c:\Users\dadidelux\Documents\Programs\mcp_explore"

# Change directory and start Flask app
Set-Location -Path "c:\Users\dadidelux\Documents\Programs\mcp_explore"
python src/meme_web_app.py
