import os
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, declarative_base

DATABASE_URL = os.enivron.get(
    "DATABASE_URL",
    "postgresql://postgres:kCxzve932;@localhost:5432/multimedia_analyzer"
)

engine = create_engine(DATABASE_URL)
SessionLocal = sessionmaker(autoflush=False, bind=engine)

Base = declarative_base()

# FastAPI Dependency to yield a DB session per request
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()