# Avian AI - Single Command Startup Script for PowerShell

Write-Host "🚀 Starting Avian AI - Bird Sound Recognition System..." -ForegroundColor Green
Write-Host "==================================================" -ForegroundColor Yellow

# Check if Python and Node.js are installed
try {
    python --version | Out-Null
    Write-Host "✅ Python found" -ForegroundColor Green
} catch {
    Write-Host "❌ Python not found. Please install Python first." -ForegroundColor Red
    exit 1
}

try {
    npm --version | Out-Null
    Write-Host "✅ npm found" -ForegroundColor Green
} catch {
    Write-Host "❌ npm not found. Please install Node.js first." -ForegroundColor Red
    exit 1
}

# Install Python dependencies if needed
Write-Host "📦 Installing Python dependencies..." -ForegroundColor Blue
Set-Location backend
if (-not (Test-Path "venv")) {
    python -m venv venv
}
& venv\Scripts\Activate.ps1
pip install -r ..\requirements.txt

# Install Node.js dependencies if needed
Write-Host "📦 Installing Node.js dependencies..." -ForegroundColor Blue
Set-Location ..\frontend
npm install

# Start backend server
Write-Host "🔧 Starting servers..." -ForegroundColor Blue
Set-Location ..\backend
$backend = Start-Process -FilePath "cmd" -ArgumentList "/k", "call venv\Scripts\activate.bat && python app.py" -PassThru

# Wait for backend to start
Write-Host "⏳ Waiting for backend to start..." -ForegroundColor Yellow
Start-Sleep -Seconds 5

# Start frontend server
Set-Location ..\frontend
$frontend = Start-Process -FilePath "cmd" -ArgumentList "/k", "npm run dev" -PassThru

# Wait for frontend to start
Write-Host "⏳ Waiting for frontend to start..." -ForegroundColor Yellow
Start-Sleep -Seconds 10

Write-Host ""
Write-Host "🎉 Avian AI is now running!" -ForegroundColor Green
Write-Host "==================================================" -ForegroundColor Yellow
Write-Host "🌐 Frontend: http://localhost:3001" -ForegroundColor Cyan
Write-Host "🔧 Backend:  http://localhost:5000" -ForegroundColor Cyan
Write-Host "📊 Health:   http://localhost:5000/health" -ForegroundColor Cyan
Write-Host ""
Write-Host "📱 Upload bird audio files to identify species!" -ForegroundColor Green
Write-Host "🔊 Audio playback is enabled" -ForegroundColor Green
Write-Host "🧠 Model confidence: 80-99%" -ForegroundColor Green
Write-Host ""
Write-Host "Press Ctrl+C to stop both servers" -ForegroundColor Yellow

# Keep script running
try {
    while ($true) {
        Start-Sleep -Seconds 1
    }
} finally {
    Write-Host ""
    Write-Host "🛑 Stopping servers..." -ForegroundColor Red
    Stop-Process -Id $backend.Id -Force -ErrorAction SilentlyContinue
    Stop-Process -Id $frontend.Id -Force -ErrorAction SilentlyContinue
    Write-Host "✅ Servers stopped" -ForegroundColor Green
}
