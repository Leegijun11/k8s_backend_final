from sqlalchemy import create_engine, text
from sqlalchemy.orm import declarative_base, sessionmaker
from app.core.config import settings

db_url = settings.DATABASE_URL
if db_url.startswith("mysql://"):
    db_url = db_url.replace("mysql://", "mysql+pymysql://")

# 1. 데이터베이스 이름이 빠진 주소로 임시 연결
root_url = db_url.rsplit("/", 1)[0] + "/"
temp_engine = create_engine(root_url)

# 2. backend-db가 없으면 ECS 컨테이너가 켜지면서 자동으로 생성
with temp_engine.connect() as conn:
    conn.execute(text("CREATE DATABASE IF NOT EXISTS `backend-db`"))
    conn.commit()
temp_engine.dispose()

# 3. 실제 서비스용 엔진 생성
engine = create_engine(db_url)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()