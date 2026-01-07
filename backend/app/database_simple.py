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
