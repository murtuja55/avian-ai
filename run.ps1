# Avian AI - Simple Startup Script

Write-Host "Starting Avian AI..." -ForegroundColor Green

# Go to backend and start it
Set-Location backend
Write-Host "Starting backend server..." -ForegroundColor Blue
Start-Process cmd -ArgumentList "/k", "python app.py"

# Wait and start frontend
Start-Sleep -Seconds 5
Set-Location ..\frontend
Write-Host "Starting frontend server..." -ForegroundColor Blue
Start-Process cmd -ArgumentList "/k", "npm run dev"

Write-Host ""
Write-Host "Avian AI is starting..." -ForegroundColor Green
Write-Host "Frontend: http://localhost:3001" -ForegroundColor Cyan
Write-Host "Backend:  http://localhost:5000" -ForegroundColor Cyan
Write-Host ""
Write-Host "Wait 10 seconds then open http://localhost:3001" -ForegroundColor Yellow
