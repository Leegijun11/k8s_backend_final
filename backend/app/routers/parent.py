#router_parents_create 양육자 등록
#router_parents_list 양육자 목록
#router_parents_delete 양육자 삭제


from typing import Optional
from urllib import response
from fastapi import APIRouter, Depends, Response, status, HTTPException, Request, Query
from sqlalchemy.ext.asyncio import AsyncSession
from pydantic import EmailStr

from app.db.database import get_db
from app.db.scheme.parents import Parent_Create
from app.services.parent import Parent_Service



router=APIRouter(prefix="/parents", tags=['Partner'])


#양육자 등록
@router.post('/add')
async def router_parents_create(parent:Parent_Create,db:AsyncSession=Depends(get_db)):
    return await Parent_Service.service_parents_create(db, parent=parent)


#양육자 목록
@router.get('/list')
async def router_parents_list(
    u_id:int=Query(..., description="유저 ID를 받아서 그룹의 멤버로 반환"),
    db:AsyncSession=Depends(get_db)):
    return await Parent_Service.service_parents_list(db, u_id=u_id)


#양육자 삭제
@router.delete('/del')
async def router_parents_delete(
    u_id:int=Query(..., description="삭제할 유저 ID"),
    db:AsyncSession=Depends(get_db)):
    return await Parent_Service.service_parents_delete(db, u_id=u_id)