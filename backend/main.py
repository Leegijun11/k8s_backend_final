from fastapi import FastAPI
from contextlib import asynccontextmanager
from app.db.database import async_engine, Base
from fastapi.middleware.cors import CORSMiddleware

from app.routers import babyimages, users, tips, logs, parent, alarm

from app.db.models.babies import Baby
from app.db.models.babycharacters import BabyCharacter
from app.db.models.care_group import Care_Group
from app.db.models.diaries import Diary
from app.db.models.records import Record


@asynccontextmanager
async def lifespan(app: FastAPI):
    async with async_engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    yield
    await async_engine.dispose()

app = FastAPI(title="Backend API", lifespan=lifespan)

# app.include_router(health.router)
# app.include_router(items.router)

@app.get("/")
async def root():
    return {"message": "home"}


app.include_router(users.router)
app.include_router(parent.router)
app.include_router(tips.router)
app.include_router(babyimages.router)
app.include_router(logs.router)
app.include_router(parent.router)
app.include_router(alarm.router)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


#uvicorn main:app --reload
