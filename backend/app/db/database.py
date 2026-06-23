from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy import create_engine, text
from sqlalchemy.orm import sessionmaker

from app.core.settings import settings

try:
    root_url = settings.sync_db_url.rsplit("/", 1)[0] + "/"

    temp_engine = create_engine(root_url)
    
    with temp_engine.connect() as conn:

        conn.execute(text("CREATE DATABASE IF NOT EXISTS backend_db"))
        conn.commit()
    temp_engine.dispose()
    print("[Database] 'backend_db' 데이터베이스 확인 및 생성 완료")
except Exception as e:
    print(f"[Database] 데이터베이스 자동 생성 절차 통과 (상태: {e})")


async_engine = create_async_engine(settings.db_url, echo=False, pool_pre_ping=True)

AsyncSessionLocal = sessionmaker(
    autocommit=False, 
    autoflush=False, 
    bind=async_engine, 
    class_=AsyncSession, 
    expire_on_commit=False
)

sync_engine = create_engine(settings.sync_db_url, pool_pre_ping=True)

Base = declarative_base()

async def get_db():
    async with AsyncSessionLocal() as session:
        try:
            yield session
            await session.commit()
        except Exception:
            await session.rollback()
            raise
        finally:
            await session.close()
