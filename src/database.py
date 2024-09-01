from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from src.models import Base  # noqa: F401

SQLALCHEMY_DATABASE_URL = "postgresql://postgres:password@db/postgres"

engine = create_engine(SQLALCHEMY_DATABASE_URL)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()