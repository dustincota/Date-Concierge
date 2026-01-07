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
