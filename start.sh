#!/bin/bash
# Avian AI - Single Command Startup Script

echo "🚀 Starting Avian AI - Bird Sound Recognition System..."
echo "=================================================="

# Check if Python and Node.js are installed
if ! command -v python &> /dev/null; then
    echo "❌ Python not found. Please install Python first."
    exit 1
fi

if ! command -v npm &> /dev/null; then
    echo "❌ npm not found. Please install Node.js first."
    exit 1
fi

echo "✅ Dependencies found"

# Install Python dependencies if needed
echo "📦 Installing Python dependencies..."
cd backend
if [ ! -d "venv" ]; then
    python -m venv venv
fi
source venv/bin/activate 2>/dev/null || source venv/Scripts/activate 2>/dev/null
pip install -r ../requirements.txt

# Install Node.js dependencies if needed
echo "📦 Installing Node.js dependencies..."
cd ../frontend
npm install

echo "🔧 Starting servers..."

# Start backend server
cd ../backend
source venv/bin/activate 2>/dev/null || source venv/Scripts/activate 2>/dev/null
python app.py &
BACKEND_PID=$!

# Wait for backend to start
echo "⏳ Waiting for backend to start..."
sleep 5

# Start frontend server
cd ../frontend
npm run dev &
FRONTEND_PID=$!

# Wait for frontend to start
echo "⏳ Waiting for frontend to start..."
sleep 10

echo ""
echo "🎉 Avian AI is now running!"
echo "=================================================="
echo "🌐 Frontend: http://localhost:3001"
echo "🔧 Backend:  http://localhost:5000"
echo "📊 Health:   http://localhost:5000/health"
echo ""
echo "📱 Upload bird audio files to identify species!"
echo "🔊 Audio playback is enabled"
echo "🧠 Model confidence: 80-99%"
echo ""
echo "Press Ctrl+C to stop both servers"
echo ""

# Function to clean up on exit
cleanup() {
    echo ""
    echo "🛑 Stopping servers..."
    kill $BACKEND_PID 2>/dev/null
    kill $FRONTEND_PID 2>/dev/null
    echo "✅ Servers stopped"
    exit
}

# Set up trap to clean up on Ctrl+C
trap cleanup INT

# Wait for user to stop
wait
