from fastapi import APIRouter, Depends, HTTPException, Request, Response
from sqlalchemy.ext.asyncio import AsyncSession
from app.db.scheme.diaries import Diary_Create, Diary_Read, Diary_List_Item, Diary_Detail, Diary_Update
from app.services.diaries import Diary_Service
from app.services.direct_diaries import Direct_Diaries_Service
from app.db.database import get_db
from app.core.auth import auth_get_u_id
from datetime import date


router = APIRouter(prefix="/diaries", tags=["Diaries"])


# 일기 생성
@router.post('/', response_model=Diary_Read)
async def router_diaries_create(
    diary: Diary_Create,
    ai_create: bool = True,
    db: AsyncSession = Depends(get_db),
    u_id: int = Depends(auth_get_u_id),
):
    if ai_create:
        return await Diary_Service.service_diaries_create(db, diary, ai_create, u_id)
    else:
        return await Direct_Diaries_Service.service_direct_diaries_create(db, diary_create=diary, u_id=u_id)


# 날짜별 일기 목록
@router.get('/', response_model=list[Diary_List_Item])
async def router_diaries_list(
    b_id: int,
    d_date: date,
    db: AsyncSession = Depends(get_db),
    u_id: int = Depends(auth_get_u_id),
):
    return await Diary_Service.service_diaries_list(db, b_id, d_date, u_id)


# 일기 상세
@router.get('/{d_id}', response_model=Diary_Detail)
async def router_diaries_detail(
    d_id: int,
    db: AsyncSession = Depends(get_db),
    u_id: int = Depends(auth_get_u_id),
):
    return await Diary_Service.service_diaries_detail(db, d_id, u_id)


# 일기 수정
@router.put('/{d_id}', response_model=Diary_Detail)
async def router_diaries_update(
    d_id: int,
    update_diary: Diary_Update,
    db: AsyncSession = Depends(get_db),
    u_id: int = Depends(auth_get_u_id),
):
    return await Diary_Service.service_diaries_update(db, d_id, update_diary, u_id)


# 일기 삭제
@router.delete('/{d_id}')
async def router_diaries_delete(
    d_id: int,
    db: AsyncSession = Depends(get_db),
    u_id: int = Depends(auth_get_u_id),
):
    return await Diary_Service.service_diaries_delete(db, d_id, u_id)