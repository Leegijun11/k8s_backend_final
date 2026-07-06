import os  # 절대 경로 처리를 위해 추가
from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles
from contextlib import asynccontextmanager
from fastapi.middleware.cors import CORSMiddleware
from app.core.scheduler import start_scheduler

from app.db.database import async_engine, Base
from app.db.models.milestones import Milestone
from app.db.models.babymilestones import BabyMilestone

from app.routers import (
    babyimages, babies, babycharacters, record, 
    users, tips, logs, parent, alarm, diaries, stories,
    milestones, health
)


@asynccontextmanager
async def lifespan(app: FastAPI):
    async with async_engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)

    start_scheduler()  

    yield
    await async_engine.dispose()


app = FastAPI(title="Backend API", lifespan=lifespan)


# CORS 설정
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173", "https://dearbaby.site"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.get("/")
async def root():
    return {"message": "home"}

app.include_router(health.router)
app.include_router(users.router)
app.include_router(parent.router)
app.include_router(tips.router)
app.include_router(babyimages.router)
app.include_router(babies.router)
app.include_router(babycharacters.router)
app.include_router(record.router)
app.include_router(logs.router)
app.include_router(alarm.router)
app.include_router(diaries.router)
app.include_router(stories.router)
app.include_router(milestones.router)


# --- 정적 파일 절대 경로 설정 추가 ---
# 현재 main.py 파일이 있는 위치의 절대 경로를 구합니다.
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
# main.py와 같은 위치에 있는 'uploads' 폴더의 전체 경로를 만듭니다.
UPLOAD_DIR = os.path.join(BASE_DIR, "uploads")

# directory 옵션에 계산된 절대 경로(UPLOAD_DIR)를 대입합니다.
app.mount("/uploads", StaticFiles(directory=UPLOAD_DIR), name="uploads")