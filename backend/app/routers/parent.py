#router_parents_create 양육자 등록
#router_parents_list 양육자 목록
#router_parents_delete 양육자 삭제


from typing import Optional
from urllib import response
from fastapi import APIRouter, Depends, Response, status, HTTPException, Request, Query
from sqlalchemy.ext.asyncio import AsyncSession
from pydantic import EmailStr

from app.db.database import get_db
from app.db.scheme.parents import Parent_Create, Parent_Update
from app.services.parent import Parent_Service
from app.core.auth import auth_get_u_id
from app.db.scheme.babies import Baby_Read

router=APIRouter(prefix="/parents", tags=['Partner'])


#양육자 등록
@router.post('/add')
async def router_parents_create(parent:Parent_Create,db:AsyncSession=Depends(get_db)):
    return await Parent_Service.service_parents_create(db, parent=parent)


#양육자 목록
@router.get('/list')
async def router_parents_list(
    u_id: int = Depends(auth_get_u_id),
    db: AsyncSession = Depends(get_db)):
    return await Parent_Service.service_parents_list(db, u_id=u_id)


# 양육자 찾기
@router.get("/find")
async def router_parents_find(u_id:int,
                              g_id:int,
                              db:AsyncSession=Depends(get_db)):
    return await Parent_Service.services_parent_find(db, u_id, g_id)

# 양육자 상태 변경
@router.put('/state')
async def router_parents_update_state(
    p_state: str,
    u_id: int = Depends(auth_get_u_id),
    db: AsyncSession = Depends(get_db)
):
    return await Parent_Service.service_parents_update_state(db, u_id, p_state)

# 양육자 수정
@router.post('/{p_id}')
async def router_parents_update(p_id:int, 
                                parent: Parent_Update,
                                db:AsyncSession=Depends(get_db)):
    return await Parent_Service.services_parent_update(db, p_id, parent)

#양육자 삭제
@router.delete('/del')
async def router_parents_delete(
    p_id:int,
    db:AsyncSession=Depends(get_db)):
    return await Parent_Service.service_parents_delete(db, p_id=p_id)

# 현재 아이 설정
@router.put('/current_baby')
async def router_parents_set_current_baby(
    b_id: int,
    u_id: int = Depends(auth_get_u_id),
    db: AsyncSession = Depends(get_db)
):
    return await Parent_Service.service_parents_set_current_baby(db, u_id, b_id)


# 현재 아이 조회
@router.get('/current_baby', response_model=Baby_Read)
async def router_parents_get_current_baby(
    u_id: int = Depends(auth_get_u_id),
    db: AsyncSession = Depends(get_db)
):
    return await Parent_Service.service_parents_get_current_baby(db, u_id)