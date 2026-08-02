#!/bin/bash
set -e

echo "🚀 Starting ASEAN Listing AI..."

# 检查后端
echo "📦 Checking backend..."
cd "$(dirname "$0")/../backend"
if [ ! -d "venv" ]; then
    echo "Creating virtual environment..."
    python3 -m venv venv
    source venv/bin/activate
    pip install -r requirements.txt
else
    source venv/bin/activate
fi

# 检查前端
echo "🎨 Checking frontend..."
cd ../frontend
if [ ! -d "node_modules" ]; then
    echo "Installing frontend dependencies..."
    npm install
fi

echo ""
echo "✅ Setup complete!"
echo ""
echo "To start the services:"
echo "  Backend:  cd backend && source venv/bin/activate && uvicorn main:app --reload --port 8000"
echo "  Frontend: cd frontend && npm run dev"
