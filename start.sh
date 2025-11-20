#!/bin/bash

# Travel Assistant - Startup Script
# This script starts both backend and frontend servers

echo "🚀 Starting Travel Planning Assistant..."
echo ""

# Check if we're in the right directory
if [ ! -d "backend" ] || [ ! -d "frontend" ]; then
    echo "❌ Error: Please run this script from the PECATHON directory"
    exit 1
fi

# Check backend dependencies
echo "📦 Checking backend dependencies..."
cd backend
if [ ! -f ".env" ]; then
    echo "Creating .env file from .env.example..."
    cp .env.example .env
fi

# Check if required Python packages are installed
python -c "import fastapi, langgraph" 2>/dev/null
if [ $? -ne 0 ]; then
    echo "Installing backend dependencies..."
    pip install -r requirements.txt
fi

echo "✓ Backend dependencies ready"
echo ""

# Check frontend dependencies
echo "📦 Checking frontend dependencies..."
cd ../frontend
if [ ! -d "node_modules" ]; then
    echo "Installing frontend dependencies..."
    npm install
fi

echo "✓ Frontend dependencies ready"
echo ""

# Start backend in background
echo "🔧 Starting backend server on http://127.0.0.1:8000..."
cd ../backend
uvicorn app.main:app --host 127.0.0.1 --port 8000 --reload > /tmp/travel-backend.log 2>&1 &
BACKEND_PID=$!
echo "Backend PID: $BACKEND_PID"

# Wait for backend to be ready
sleep 3

# Check if backend is running
if ! kill -0 $BACKEND_PID 2>/dev/null; then
    echo "❌ Backend failed to start. Check /tmp/travel-backend.log for errors"
    cat /tmp/travel-backend.log
    exit 1
fi

echo "✓ Backend started successfully"
echo ""

# Start frontend
echo "🎨 Starting frontend server on http://localhost:5173..."
cd ../frontend
npm run dev &
FRONTEND_PID=$!
echo "Frontend PID: $FRONTEND_PID"

echo ""
echo "✅ Application is starting!"
echo ""
echo "Backend:  http://127.0.0.1:8000"
echo "Frontend: http://localhost:5173"
echo "Health:   http://127.0.0.1:8000/health"
echo ""
echo "Backend logs: /tmp/travel-backend.log"
echo ""
echo "Press Ctrl+C to stop all servers"
echo ""

# Handle Ctrl+C
trap "echo ''; echo '🛑 Stopping servers...'; kill $BACKEND_PID $FRONTEND_PID 2>/dev/null; exit 0" INT

# Wait for frontend process
wait $FRONTEND_PID
