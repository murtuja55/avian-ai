# Avian AI - Fixed Startup Script

Write-Host "Starting Avian AI..." -ForegroundColor Green

# Kill existing processes
Write-Host "Stopping existing servers..." -ForegroundColor Yellow
taskkill /F /IM node.exe 2>$null
taskkill /F /IM python.exe 2>$null
Start-Sleep -Seconds 2

# Go to project root
Set-Location $PSScriptRoot

# Start backend
Write-Host "Starting backend..." -ForegroundColor Blue
Set-Location backend
Start-Process cmd -ArgumentList "/k", "python app.py"

# Wait and start frontend
Start-Sleep -Seconds 5
Write-Host "Starting frontend..." -ForegroundColor Blue
Set-Location ..\frontend
Start-Process cmd -ArgumentList "/k", "npm run dev"

Write-Host ""
Write-Host "Avian AI is starting..." -ForegroundColor Green
Write-Host "Frontend: http://localhost:3001" -ForegroundColor Cyan
Write-Host "Backend:  http://localhost:5000" -ForegroundColor Cyan
Write-Host ""
Write-Host "Wait 10 seconds then open http://localhost:3001" -ForegroundColor Yellow
