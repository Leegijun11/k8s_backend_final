import os  # 절대 경로 처리를 위해 추가
from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles
from contextlib import asynccontextmanager
from fastapi.middleware.cors import CORSMiddleware
from app.core.scheduler import start_scheduler

from app.db.database import async_engine, Base
from app.db.models.milestones import Milestone
from app.db.models.babymilestones import BabyMilestone

# Models
from app.db.models.alarms import Alarm
from app.db.models.babies import Baby
from app.db.models.babycharacters import BabyCharacter
from app.db.models.care_group import Care_Group
from app.db.models.diaries import Diary
from app.db.models.parents import Parent
from app.db.models.records import Record
from app.db.models.stories import Story
from app.db.models.forums import Forums
from app.db.models.forumlikes import ForumLike
from app.db.models.forumtags import ForumTag
from app.db.models.forumcomments import ForumComment
from app.db.models.forumcommentlikes import ForumCommentLike
# Routers

from app.routers import (
    babyimages, babies, babycharacters, record, 
    users, tips, logs, parent, alarm, diaries, stories,
    milestones, forum, forumlikes, forumcomments, forumcommentlikes, health
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
    allow_origins=["http://localhost:5173", "https://dearbaby.site", "http://127.0.0.1:5173"],
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
app.include_router(forum.router)
app.include_router(forumlikes.router)
app.include_router(milestones.router)
app.include_router(forumcomments.router)
app.include_router(forumcommentlikes.router)

# app.mount("/uploads", StaticFiles(directory="uploads"), name="uploads")
# # uvicorn main:app --reload

# --- 정적 파일 절대 경로 설정 추가 ---
# 현재 main.py 파일이 있는 위치의 절대 경로를 구합니다.
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
# main.py와 같은 위치에 있는 'uploads' 폴더의 전체 경로를 만듭니다.
UPLOAD_DIR = os.path.join(BASE_DIR, "uploads")

# directory 옵션에 계산된 절대 경로(UPLOAD_DIR)를 대입합니다.
app.mount("/uploads", StaticFiles(directory=UPLOAD_DIR), name="uploads")
