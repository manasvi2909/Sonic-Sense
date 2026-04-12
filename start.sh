#!/bin/bash
echo "Starting SonicSense..."

# Start FastAPI backend
echo "Starting FastAPI backend on port 8000..."
source .venv/bin/activate
uvicorn api.main:app --host 0.0.0.0 --port 8000 --reload &
BACKEND_PID=$!

# Start Vite React frontend
echo "Starting React frontend on port 3000..."
cd frontend
source ~/.nvm/nvm.sh
nvm use 20
npm run dev -- --host 0.0.0.0 --port 3000 &
FRONTEND_PID=$!

echo "SonicSense running."
echo "Backend: http://localhost:8000"
echo "Frontend: http://localhost:3000"
echo "Press Ctrl+C to stop both servers."

trap "kill $BACKEND_PID $FRONTEND_PID" EXIT
wait
