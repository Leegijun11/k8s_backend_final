#router_stories_create : 디지털북 생성
#router_stories_list : b_id별 디지털북 목록
#router_stories_detail : 디지털북 상세
#router_stories_delete : 디지털북 삭제

from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession

from app.db.scheme.stories import Story_Create, Story_Read
from app.services.stories import Story_Service

from app.db.scheme.story_pages import Story_Page_Create, Story_Page_Read

from app.db.database import get_db


router = APIRouter(prefix="/stories", tags=["Stories"])


# 디지털북 생성
@router.post('/create', response_model=Story_Read)
async def router_stories_create(story: Story_Create, db: AsyncSession = Depends(get_db)):
    return await Story_Service.service_stories_create(db, story)


# b_id별 디지털북 목록
@router.get('/list', response_model=list[Story_Read])
async def router_stories_list(b_id: int, db: AsyncSession = Depends(get_db)):
    return await Story_Service.service_stories_list(db, b_id)


# 디지털북 삭제
@router.delete('/del/{s_id}')
async def router_stories_delete(s_id: int, db: AsyncSession = Depends(get_db)):
    return await Story_Service.service_stories_delete(db, s_id)


# 디지털북 상세
@router.get('/{s_id}', response_model=Story_Read)
async def router_stories_detail(s_id: int, db: AsyncSession = Depends(get_db)):
    return await Story_Service.service_stories_detail(db, s_id)


# 디지털북 페이지 목록
@router.get('/page/list/{s_id}', response_model=list[Story_Page_Read])
async def router_stories_pages_list(s_id : int, db: AsyncSession = Depends(get_db)):
    return await Story_Service.service_stories_pages_list(db, s_id)

# 디지털북 페이지 상세
@router.get('/page/{sp_id}', response_model=Story_Page_Read)
async def router_stories_pages_detail(sp_id : int, db: AsyncSession = Depends(get_db)):
    return await Story_Service.service_stories_pages_detail(db, sp_id)

# 디지털북 페이지 삭제
@router.get('/page/del')
async def router_stories_pages_del(sp_id : int, db: AsyncSession = Depends(get_db)):
    return await Story_Service.service_stories_pages_del(db, sp_id)

