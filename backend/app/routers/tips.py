#router_tips_list 팁 목록
#router_tips_info 팁 상세 내용


from typing import Optional
from urllib import response
from fastapi import APIRouter, Depends, Response, status, HTTPException, Request, Query
from sqlalchemy.ext.asyncio import AsyncSession
from pydantic import EmailStr
from app.db.database import get_db
from app.db.scheme.tips import Tip_Read
from app.services.tips import Tip_Service


router=APIRouter(prefix="/tips",tags=["Tips"])


#팁 목록
@router.get('/list', response_model=list[Tip_Read])
async def router_tips_list(t_age:Optional[int]=Query(None), skip:int=Query(0), limit:int=Query(10), db:AsyncSession=Depends(get_db)):
    return await Tip_Service.service_tip_list(db, t_age=t_age, skip=skip, limit=limit)

#팁 상세 내용 조회
@router.get('/{t_id}', response_model=Tip_Read)
async def router_tips_detail(t_id:int, db:AsyncSession=Depends(get_db)):
    return await Tip_Service.service_tips_info(db, t_id=t_id)