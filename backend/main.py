import os
from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles
from contextlib import asynccontextmanager
from fastapi.middleware.cors import CORSMiddleware
from app.core.scheduler import start_scheduler

from app.db.database import async_engine, Base
from app.db.models.milestones import Milestone
from app.db.models.babymilestones import BabyMilestone
from app.db.models.standards import BabyStandard

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
    forum, forumlikes, forumcomments, forumcommentlikes, health,
    milestones, standards,
    secure_images,  # ★ 인증/인가를 거치는 이미지 라우터 추가
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
app.include_router(forum.router)
app.include_router(forumlikes.router)
app.include_router(milestones.router)
app.include_router(forumcomments.router)
app.include_router(forumcommentlikes.router)
app.include_router(standards.router)
app.include_router(secure_images.router)  # ★ 이미지 보호 라우터 등록

# --- 정적 파일(Static Files) 설정 ---
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
UPLOAD_DIR = os.path.join(BASE_DIR, "uploads")


# 예전 코드:
#   app.mount("/uploads", StaticFiles(directory=UPLOAD_DIR), name="uploads")
#   app.mount("/images", StaticFiles(directory=IMAGES_DIR), name="images")

# forum_images는 커뮤니티 게시글용이라 공개 유지 (필요 시 이것도 보호 라우터로 전환 가능)
FORUM_IMAGES_DIR = os.path.join(UPLOAD_DIR, "forum_images")
if not os.path.exists(FORUM_IMAGES_DIR):
    os.makedirs(FORUM_IMAGES_DIR)

app.mount("/uploads/forum_images", StaticFiles(directory=FORUM_IMAGES_DIR), name="forum_images")
app.mount("/cover", StaticFiles(directory="cover"), name="cover")