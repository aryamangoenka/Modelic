#!/bin/bash

echo "🚀 Starting MLOps Platform Development Environment"
echo "=================================================="

# Start FastAPI backend
echo "📡 Starting FastAPI Backend on port 8000..."
cd "$(dirname "$0")"
python run.py &
BACKEND_PID=$!

# Wait a moment for backend to start
sleep 3

# Start Next.js frontend
echo "🎨 Starting Next.js Frontend on port 3000..."
cd frontend
npm run dev &
FRONTEND_PID=$!

echo ""
echo "✅ Development environment started!"
echo "📡 Backend API: http://localhost:8000"
echo "📚 API Docs: http://localhost:8000/docs"
echo "🎨 Frontend: http://localhost:3000"
echo ""
echo "Press Ctrl+C to stop both services"

# Wait for Ctrl+C and then kill both processes
trap "echo '🛑 Stopping services...'; kill $BACKEND_PID $FRONTEND_PID; exit" INT
wait 