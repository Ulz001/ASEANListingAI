#!/bin/bash
set -e

echo "🚀 Starting ASEAN Listing AI..."

# 启动后端
echo "📦 Starting backend on port 8000..."
cd "$(dirname "$0")/../backend"
source venv/bin/activate
uvicorn main:app --host 0.0.0.0 --port 8000 --reload &
BACKEND_PID=$!

# 启动前端
echo "🎨 Starting frontend on port 8080..."
cd ../frontend
npm run dev &
FRONTEND_PID=$!

echo ""
echo "✅ Services started!"
echo "  Backend:  http://localhost:8000"
echo "  Frontend: http://localhost:8080"
echo "  API Docs: http://localhost:8000/docs"
echo ""
echo "Press Ctrl+C to stop all services"

# 等待中断信号
trap "kill $BACKEND_PID $FRONTEND_PID 2>/dev/null; exit" INT TERM
wait
