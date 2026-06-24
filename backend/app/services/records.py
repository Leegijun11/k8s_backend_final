from sqlalchemy.ext.asyncio import AsyncSession
from app.db.scheme.records import Record_Create, Record_Update
from app.db.crud.records import Record_Crud, Record_Crud
from app.db.crud.babies import Baby_Crud 
from datetime import datetime
from fastapi import HTTPException

class RecordService:

    # 1. 성장기록 등록
    @staticmethod
    async def service_records_create(record:Record_Create, db:AsyncSession):
        if record.r_height <= 0 or record.r_weight <= 0:
            raise  HTTPException(status_code=400, detail="키와 몸무게는 0보다 커야 합니다.")
        try:
            db_data=await Record_Crud.crud_records_create(db, record)
            await db.commit()
            await db.refresh(db_data)
            return db_data
        except Exception as e:
            await db.rollback()
            raise HTTPException(status_code=400, detail="성장기록 정보 등록에 실패했습니다.")
    
    # 2. 성장기록 조회
    @staticmethod
    async def service_records_list(b_id:int, start_date:datetime, end_date:datetime, db:AsyncSession):
        try:
            exist_baby=await Baby_Crud.crud_babies_detail(db, b_id)
        except Exception as e:
            raise HTTPException(status_code=500, detail="성장기록을 조회하는 중 오류가 발생했습니다.")
        if exist_baby is None:
            raise HTTPException(status_code=404, detail="해당 아기 정보를 찾을 수 없습니다.")

        try:
            db_data=await Record_Crud.crud_records_details(db, b_id, start_date, end_date)
            return db_data
        except Exception as e:
            raise HTTPException(status_code=500, detail="성장기록 목록을 불러오는데 실패했습니다.")
        
    # 3. 성장기록 수정
    @staticmethod
    async def service_records_update(r_id:int, record:Record_Update, db:AsyncSession):
            if (record.r_height is not None and record.r_height <= 0) or \
               (record.r_weight is not None and record.r_weight <= 0):
                raise HTTPException(status_code=400, detail="키와 몸무게는 0보다 커야 합니다.")
            
            try:
                db_data=await Record_Crud.crud_records_update(db, r_id, record)
            except Exception as e:
                raise HTTPException(status_code=500, detail="성장기록 수정 중 오류가 발생했습니다.")
            
            if db_data is None:
                raise HTTPException(status_code=404, detail="수정할 성장기록을 찾을 수 없습니다.")
                
            try:
                await db.commit()
                await db.refresh(db_data)
                return db_data
            except Exception as e:
                await db.rollback()
                raise HTTPException(status_code=500, detail="성장기록 수정 내용을 저장하는데 실패했습니다.")
            
    # 4. 성장기록 삭제
    @staticmethod
    async def service_records_delete(r_id:int, db:AsyncSession):
        try:
            db_data=await Record_Crud.crud_records_del(db, r_id)
        except Exception as e:
            raise HTTPException(status_code=500, detail="성장기록 삭제 중 오류가 발생했습니다.")
        
        if db_data is None:
            raise HTTPException(status_code=404, detail="삭제할 성장기록이 존재하지 않습니다.")
        
        try:
            await db.commit()
            return db_data
        except Exception as e:
            await db.rollback()
            raise HTTPException(status_code=404, detail="성장기록 삭제 내용을 반영하는데 실패했습니다.")