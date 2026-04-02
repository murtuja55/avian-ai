@echo off
REM Avian AI - Single Command Startup Script for Windows

echo 🚀 Starting Avian AI - Bird Sound Recognition System...
echo ==================================================

REM Check if Python and Node.js are installed
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

echo ✅ Dependencies found

REM Install Python dependencies if needed
echo 📦 Installing Python dependencies...
cd backend
if not exist "venv" (
    python -m venv venv
)
call venv\Scripts\activate
pip install -r ..\requirements.txt

REM Install Node.js dependencies if needed
echo 📦 Installing Node.js dependencies...
cd ..\frontend
npm install

echo 🔧 Starting servers...

REM Start backend server
cd ..\backend
start "Backend Server" cmd /k "call venv\Scripts\activate && python app.py"

REM Wait for backend to start
echo ⏳ Waiting for backend to start...
timeout /t 5 /nobreak >nul

REM Start frontend server
cd ..\frontend
start "Frontend Server" cmd /k "npm run dev"

REM Wait for frontend to start
echo ⏳ Waiting for frontend to start...
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
echo Press any key to stop servers...
pause

REM Stop servers (close the windows)
taskkill /f /im python.exe >nul 2>&1
taskkill /f /im node.exe >nul 2>&1
echo ✅ Servers stopped
