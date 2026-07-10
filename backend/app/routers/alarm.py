from typing import Optional
from urllib import response
from fastapi import APIRouter, Depends, Response, status, HTTPException, Request, Query
from sqlalchemy.ext.asyncio import AsyncSession
from pydantic import EmailStr

from app.db.database import get_db
from app.db.scheme.alarms import Alarm_Create
from app.services.alarm import Alarm_Service
from app.db.scheme.users import User_Base
from app.core.auth import auth_get_u_id

router = APIRouter(prefix="/alarms", tags=['Alarm'])


# 알람 추가 (p_category 파라미터 추가)
@router.post("/create")
async def router_alarm_create(
    receive_account: str, 
    p_category: str, 
    send_id: int = Depends(auth_get_u_id), 
    db: AsyncSession = Depends(get_db)
):
    return await Alarm_Service.service_alarm_create(
        db, 
        send_id=send_id, 
        receive_account=receive_account, 
        p_category=p_category
    )


# 내 알람 목록
@router.get("/list")
async def router_alarm_list(receive_id: int = Depends(auth_get_u_id), db: AsyncSession = Depends(get_db)):
    return await Alarm_Service.service_alarm_list(db, receive_id=receive_id)


# 알람 삭제
@router.delete("/delete")
async def router_alarm_delete(a_id: int, db: AsyncSession = Depends(get_db)):
    return await Alarm_Service.service_alarm_delete(db, a_id=a_id)


# 알람 전체 삭제
@router.delete("/all_del")
async def router_alarm_all_del(receive_id: int = Depends(auth_get_u_id), db: AsyncSession = Depends(get_db)):
    return await Alarm_Service.service_alarm_all_del(db, receive_id)