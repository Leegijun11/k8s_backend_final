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
    milestones
)


@asynccontextmanager
async def lifespan(app: FastAPI):
    async with async_engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)

    start_scheduler()   # 서버 시작 시 스케줄러도 같이 시작

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
app.include_router(milestones.router)

app.mount("/uploads", StaticFiles(directory="uploads"), name="uploads")