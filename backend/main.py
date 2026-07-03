import os
from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles
from contextlib import asynccontextmanager
from fastapi.middleware.cors import CORSMiddleware
from app.core.scheduler import start_scheduler

from app.db.database import async_engine, Base
from app.db.models.milestones import Milestone
from app.db.models.babymilestones import BabyMilestone
# ★ 표준 모델 테이블 싱크를 위해 임포트 (기존 임포트 하단에 추가)
from app.db.models.standards import BabyStandard 

from app.routers import (
    babyimages, babies, babycharacters, record, 
    users, tips, logs, parent, alarm, diaries, stories,
    milestones, health, standards  # ★ standards 라우터 추가
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

# 라우터 등록
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
app.include_router(standards.router)  # ★ standards 라우터 추가


# --- 정적 파일(Static Files) 설정 ---
BASE_DIR = os.path.dirname(os.path.abspath(__file__))

# 1. 기존 uploads 폴더 마운트
UPLOAD_DIR = os.path.join(BASE_DIR, "uploads")
app.mount("/uploads", StaticFiles(directory=UPLOAD_DIR), name="uploads")

# 2. 상위 폴더의 실제 아기 사진 images 폴더 마운트 (완벽함!)
PARENT_DIR = os.path.dirname(BASE_DIR)
IMAGES_DIR = os.path.join(PARENT_DIR, "images")

if not os.path.exists(IMAGES_DIR):
    os.makedirs(IMAGES_DIR)

app.mount("/images", StaticFiles(directory=IMAGES_DIR), name="images")