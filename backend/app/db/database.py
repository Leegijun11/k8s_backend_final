from sqlalchemy import create_engine
from sqlalchemy.orm import declarative_base, sessionmaker
from app.core.config import settings


db_url = settings.DATABASE_URL
if db_url.startswith("mysql://"):
    db_url = db_url.replace("mysql://", "mysql+pymysql://")


engine = create_engine(db_url)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()