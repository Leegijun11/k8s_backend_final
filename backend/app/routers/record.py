from fastapi import APIRouter, Depends, HTTPException, Body, Query
from sqlalchemy.ext.asyncio import AsyncSession
from app.db.database import get_db 
from app.db.scheme.records import Record_Create, Record_Update, Record_Read
from app.services.records import RecordService
from datetime import datetime

router=APIRouter(prefix="/records", tags=["Record"])

# 1. 성장기록 등록
@router.post("/create", response_model=Record_Read)
async def routers_record_create(record:Record_Create, db:AsyncSession=Depends(get_db)):
    db_data=await RecordService.service_records_create(record, db)
    return db_data
    
# 2. 성장기록 정보 조회
@router.get("/list", response_model=list[Record_Read])
async def routers_record_list(b_id:int, start_date:datetime, end_date:datetime, db:AsyncSession=Depends(get_db)):
    db_data=await RecordService.service_records_list(b_id, start_date, end_date, db)
    return db_data

# 3. 성장기록 수정
@router.put("/{r_id}", response_model=Record_Read)
async def routers_record_update(r_id:int, record:Record_Update, db:AsyncSession=Depends(get_db)):
    db_data=await RecordService.service_records_update(r_id, record, db)
    return db_data
    
# 4. 성장기록 삭제
@router.delete("/del", response_model=Record_Read)
async def routers_record_delete(r_id:int, db:AsyncSession=Depends(get_db)):
    db_data=await RecordService.service_records_delete(r_id, db)
    return db_data