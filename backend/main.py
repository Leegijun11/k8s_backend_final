from fastapi import FastAPI
from contextlib import asynccontextmanager
from app.routers import babyimages, babies, babycharacters, record, diaries
from app.db.database import async_engine, Base
from fastapi.middleware.cors import CORSMiddleware

from app.routers import babies, babycharacters, record, diaries

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
app.include_router(babies.router)
app.include_router(babycharacters.router)
app.include_router(record.router)
app.include_router(diaries.router)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
