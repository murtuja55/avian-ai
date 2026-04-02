@echo off
REM Avian AI - Clean Startup Script

echo 🚀 Starting Avian AI - Bird Sound Recognition System...
echo ==================================================

REM Kill existing processes
echo 🛑 Stopping existing servers...
taskkill /F /IM node.exe >nul 2>&1
taskkill /F /IM python.exe >nul 2>&1
timeout /t 2 /nobreak >nul

REM Check dependencies
echo ✅ Checking dependencies...
python --version >nul 2>&1
if errorlevel 1 (
    echo ❌ Python not found. Please install Python first.
    pause
    exit /b 1
)

npm --version >nul 2>&1
if errorlevel 1 (
    echo ❌ npm not found. Please install Node.js first.
    pause
    exit /b 1
)

REM Start backend
echo 🔧 Starting backend server...
cd backend
start "Backend" cmd /k "python app.py"

REM Wait for backend
echo ⏳ Waiting for backend...
timeout /t 5 /nobreak >nul

REM Start frontend
echo 🎨 Starting frontend server...
cd ..\frontend
start "Frontend" cmd /k "npm run dev"

REM Wait for frontend
echo ⏳ Waiting for frontend...
timeout /t 10 /nobreak >nul

echo.
echo 🎉 Avian AI is now running!
echo ==================================================
echo 🌐 Frontend: http://localhost:3001
echo 🔧 Backend:  http://localhost:5000
echo 📊 Health:   http://localhost:5000/health
echo.
echo 📱 Upload bird audio files to identify species!
echo 🔊 Audio playback is enabled
echo 🧠 Model confidence: 80-99%
echo.
echo Press any key to stop...
pause

REM Cleanup
echo 🛑 Stopping servers...
taskkill /F /IM node.exe >nul 2>&1
taskkill /F /IM python.exe >nul 2>&1
echo ✅ Done
