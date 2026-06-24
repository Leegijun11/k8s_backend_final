#router_stories_create : 디지털북 생성

from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession
from app.db.scheme.stories import Story_Create, Story_Read
from app.services.stories import Story_Service
from app.db.database import get_db


router = APIRouter(prefix="/stories", tags=["Stories"])


# 디지털북 생성
@router.post('/create', response_model=Story_Read)
async def router_stories_create(story: Story_Create, db: AsyncSession = Depends(get_db)):
    return await Story_Service.service_stories_create(db, story)