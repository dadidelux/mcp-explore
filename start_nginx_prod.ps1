# start_nginx_prod.ps1
Write-Host "Starting Nginx Production Server..." -ForegroundColor Green

# Stop any existing containers
Write-Host "Stopping existing containers..." -ForegroundColor Yellow
docker-compose down --remove-orphans

# Build and start the services
Write-Host "Building and starting services..." -ForegroundColor Green
docker-compose up --build -d

# Wait for services to start
Write-Host "Waiting for services to initialize..." -ForegroundColor Yellow
Start-Sleep -Seconds 10

# Show service status
Write-Host "Service Status:" -ForegroundColor Cyan
docker-compose ps

Write-Host "`nApplication is running at: http://localhost" -ForegroundColor Green
Write-Host "Use 'docker-compose logs -f' to see logs" -ForegroundColor Yellow
Write-Host "Use '.\stop_nginx_production.ps1' to stop the server" -ForegroundColor Yellow

# Open in browser
Start-Process "http://localhost"
