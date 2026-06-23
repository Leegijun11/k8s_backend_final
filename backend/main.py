from fastapi import FastAPI
from contextlib import asynccontextmanager
from app.routers import babyimages
from app.db.database import async_engine, Base
from fastapi.middleware.cors import CORSMiddleware


from app.db.models.alarms import Alarm
from app.db.models.babies import Baby
from app.db.models.babycharacters import BabyCharacter
from app.db.models.care_group import Care_Group
from app.db.models.diaries import Diary
from app.db.models.parents import Parent
from app.db.models.records import Record
from app.db.models.users import User

@asynccontextmanager
async def lifespan(app: FastAPI):
    async with async_engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    yield
    await async_engine.dispose()

app = FastAPI(title="Backend API", lifespan=lifespan)

# app.include_router(health.router)
# app.include_router(items.router)
app.include_router(babyimages.router)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
