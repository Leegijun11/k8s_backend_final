from fastapi import APIRouter, Depends, status
from sqlalchemy.ext.asyncio import AsyncSession
from app.db.database import get_db
from app.db.scheme.logs import Log_Create, Log_Read, Log_Update
from app.services.logs import Log_Service

router=APIRouter(prefix='/logs',tags=['Log'])


# POST 기록 생성
@router.post('/add',response_model=Log_Read)
async def router_logs_add(log : Log_Create, 
                          db : AsyncSession=Depends(get_db)):
    return await Log_Service.services_logs_create(db, log)


# GET 기록 상세
@router.get('/detail', response_model=Log_Read | None)
async def router_logs_detail(l_id: int, 
                             db : AsyncSession=Depends(get_db)):
    return await Log_Service.services_logs_detail(db, l_id)


# POST 기록 수정
@router.post('/edit',response_model=Log_Read)
async def router_logs_edit(log : Log_Update,
                           l_id : int,
                           db : AsyncSession=Depends(get_db)):
    return await Log_Service.services_logs_update(db, l_id, log)


# DELETE 현재 기록 삭제
@router.delete("/del")
async def router_logs_del(l_id:int,
                          db: AsyncSession = Depends(get_db)):
    return await Log_Service.services_logs_del(db, l_id)


# 기록 목록
@router.get('/list', response_model=list[Log_Read])
async def router_logs_list(b_id: int, db: AsyncSession = Depends(get_db)):
    return await Log_Service.services_logs_list(db, b_id)