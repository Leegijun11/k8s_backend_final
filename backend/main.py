from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles
from contextlib import asynccontextmanager
from fastapi.middleware.cors import CORSMiddleware

# DB 및 엔진
from app.db.database import async_engine, Base
# 새로운 모델을 여기서 반드시 import 해야 테이블이 생성됩니다!
from app.db.models.milestones import Milestone
from app.db.models.babymilestones import BabyMilestone

# Routers
from app.routers import (
    babyimages, babies, babycharacters, record, 
    users, tips, logs, parent, alarm, diaries, stories,
    milestones # 새로 만든 라우터도 추가
)

@asynccontextmanager
async def lifespan(app: FastAPI):
    async with async_engine.begin() as conn:
        # Base를 상속받은 모든 모델이 import 되어 있어야 여기서 테이블이 생성됩니다.
        await conn.run_sync(Base.metadata.create_all)
    yield
    await async_engine.dispose()

app = FastAPI(title="Backend API", lifespan=lifespan)

# CORS 설정
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.get("/")
async def root():
    return {"message": "home"}

# Router 등록
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
app.include_router(milestones.router) # 라우터 등록

app.mount("/uploads", StaticFiles(directory="uploads"), name="uploads")