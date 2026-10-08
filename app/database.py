from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from app.config import settings
#DATABASE_URL = "postgresql://postgres:postgres@localhost:5432/loan_db"
engine = create_engine(settings.database_url)
SessionLocal = sessionmaker(autocommit=False, 
                            autoflush=False, 
                            bind=engine)
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()