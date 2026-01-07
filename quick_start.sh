#!/bin/bash

# Date Concierge - Quick Local Setup (No Docker Required)
# Run this to start the app locally for development/demo

set -e

echo "🎬 Date Concierge - Quick Local Setup"
echo "====================================="
echo ""

# Check if Python is installed
if ! command -v python3 &> /dev/null; then
    echo "❌ Python 3 is required but not installed."
    echo "   Install from: https://www.python.org/downloads/"
    exit 1
fi

# Check if Node.js is installed
if ! command -v node &> /dev/null; then
    echo "❌ Node.js is required but not installed."
    echo "   Install from: https://nodejs.org/"
    exit 1
fi

echo "✓ Python 3 found: $(python3 --version)"
echo "✓ Node.js found: $(node --version)"
echo ""

# Setup .env if it doesn't exist
if [ ! -f .env ]; then
    echo "📝 Creating .env file..."
    cp .env.example .env
    echo "✓ Created .env (you can add API keys later)"
    echo ""
fi

# Install backend dependencies
echo "📦 Installing backend dependencies..."
cd backend
if [ ! -d "venv" ]; then
    python3 -m venv venv
fi
source venv/bin/activate || . venv/Scripts/activate  # Windows compatibility
pip install -q -r requirements.txt
echo "✓ Backend dependencies installed"
echo ""

# Setup SQLite database (simpler than PostgreSQL for demo)
echo "🗄️  Setting up database..."
cat > app/database_simple.py << 'EOF'
"""Simple SQLite database for local development."""
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from app.database import Base

# Use SQLite instead of PostgreSQL for local demo
SQLALCHEMY_DATABASE_URL = "sqlite:///./date_concierge.db"

engine = create_engine(
    SQLALCHEMY_DATABASE_URL, connect_args={"check_same_thread": False}
)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

def init_db():
    """Create all tables."""
    Base.metadata.create_all(bind=engine)
    print("✓ Database tables created")

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
EOF

# Update config to use SQLite
echo "✓ Database configured (SQLite)"
echo ""

# Create simple startup script
cat > start_backend.py << 'EOF'
"""Start the backend server."""
import sys
sys.path.insert(0, '.')

# Initialize database
from app.database_simple import init_db
init_db()

# Seed venues
print("🌱 Seeding venues...")
from app.seed_data import seed_venues
from app.database_simple import SessionLocal
db = SessionLocal()
seed_venues(db)
db.close()

print("")
print("✅ Backend ready!")
print("📡 Starting API server on http://localhost:8080")
print("📚 API docs at http://localhost:8080/docs")
print("")

# Start uvicorn
import uvicorn
uvicorn.run("app.main:app", host="0.0.0.0", port=8080, reload=True)
EOF

cd ..

# Install frontend dependencies
echo "📦 Installing frontend dependencies..."
cd frontend
if [ ! -d "node_modules" ]; then
    npm install
fi
echo "✓ Frontend dependencies installed"
echo ""

cd ..

echo "✅ Setup Complete!"
echo ""
echo "═══════════════════════════════════════"
echo "🚀 Starting Date Concierge..."
echo "═══════════════════════════════════════"
echo ""
echo "Terminal 1 (Backend): cd backend && python3 start_backend.py"
echo "Terminal 2 (Frontend): cd frontend && npm run dev"
echo ""
echo "Then open: http://localhost:5173"
echo ""
echo "═══════════════════════════════════════"
echo ""

# Ask if user wants to start now
read -p "Start the application now? (y/n) " -n 1 -r
echo
if [[ $REPLY =~ ^[Yy]$ ]]; then
    echo "Starting backend..."
    cd backend
    python3 start_backend.py &
    BACKEND_PID=$!

    echo "Starting frontend..."
    cd ../frontend
    npm run dev &
    FRONTEND_PID=$!

    echo ""
    echo "✅ Application started!"
    echo "🌐 Open http://localhost:5173 in your browser"
    echo ""
    echo "Press Ctrl+C to stop"

    # Wait for user to stop
    wait
else
    echo "Run these commands in separate terminals:"
    echo "  Terminal 1: cd backend && python3 start_backend.py"
    echo "  Terminal 2: cd frontend && npm run dev"
fi
