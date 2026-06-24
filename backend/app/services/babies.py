from sqlalchemy.ext.asyncio import AsyncSession
from app.db.scheme.babies import Baby_Create, Baby_Update
from app.db.scheme.care_groups import CareGroup_Create
from app.db.crud.babies import Baby_Crud
from app.db.crud.care_groups import CareGroup_Crud
from app.db.crud.records import Record_Crud
from app.db.scheme.records import Record_Create
from datetime import datetime
from fastapi import HTTPException
from argparse import Namespace

class BabyService:

    # 1. 아이 정보 등록
    @staticmethod
    async def service_babies_create(u_id: int, baby: Baby_Create, db: AsyncSession):
        if baby.b_height <= 0 or baby.b_weight <= 0:
            raise HTTPException(status_code=400, detail="키와 몸무게는 0보다 커야 합니다.")
        try:
            new_group = CareGroup_Create(creator_id=u_id) 
            care_group = await CareGroup_Crud.crud_caregroups_create(db, new_group) 
            
            baby_dict = baby.model_dump()
            baby_dict["g_id"] = care_group.g_id  
            
            db_baby = await Baby_Crud.crud_babies_create(db, baby_dict) 

            await db.commit()
            await db.refresh(db_baby)
            
            return db_baby
            
        except Exception as e:
            await db.rollback()  
            raise HTTPException(status_code=400, detail=f"{e}아이 정보 등록에 실패했습니다.")

    # 2. 아이 목록 조회
    @staticmethod
    async def service_babies_list(u_id:int, db:AsyncSession):
        try:
            db_data=await Baby_Crud.crud_babies_list(db, u_id)
            return db_data
        except Exception as e:
            print(f"아미 목록 조회 에러 : {e}")
            raise HTTPException(status_code=500, detail="아이들의 정보를 불러오는 중 서버 오류가 발생했습니다.")        

        
    # 3. 아이 세부 정보
    @staticmethod
    async def service_babies_read(b_id:int, db: AsyncSession):
        try:
            db_data=await Baby_Crud.crud_babies_detail(b_id, db)
            if db_data is None:
                raise HTTPException(status_code=400, detail="아이의 정보를 불러오는데 실패했습니다.")
            return db_data
        except Exception as e:
            raise HTTPException(status_code=400, detail="아이의 정보를 불러오는데 실패했습니다.")
        

    # 4. 아이 정보 수정(추가)
    @staticmethod
    async def service_babies_update(b_id:int, baby:Baby_Update, db:AsyncSession):
        if (baby.b_height is not None and baby.b_height <= 0) or \
           (baby.b_weight is not None and baby.b_weight <= 0):
            raise HTTPException(status_code=400, detail="키와 몸무게는 0보다 커야 합니다.")
            
        try:
            exist_baby = await Baby_Crud.crud_babies_detail(b_id, db)
            if exist_baby is None:
                raise HTTPException(status_code=400, detail="아이의 정보를 수정하는데 실패했습니다.")
            
            past_record = Record_Create(
                b_id=exist_baby.b_id,
                r_height=exist_baby.b_height,
                r_weight=exist_baby.b_weight
            )

            await Record_Crud.crud_records_create(db, past_record)
            
            db_data = await Baby_Crud.crud_babies_update(db, b_id, baby)
            if db_data is None:
                raise HTTPException(status_code=400, detail="아이의 정보를 수정하는데 실패했습니다.")
            
            await db.commit()
            await db.refresh(db_data)
            
            return db_data
            
        except Exception as e:
            await db.rollback()
            raise HTTPException(status_code=400, detail="아이의 정보를 수정하는데 실패했습니다.")

    # 5. 아이 정보 삭제
    @staticmethod
    async def service_babies_delete(b_id:int, db: AsyncSession):
        try:
            exist_baby=await Baby_Crud.crud_babies_detail(b_id, db)
            if exist_baby is None:
                raise HTTPException(status_code=400, detail="아이의 정보를 삭제하는데 실패했습니다.")
            db_data=await Baby_Crud.crud_babies_del(b_id, db)
            return db_data
        except Exception as e:
            raise HTTPException(status_code=400, detail="아이의 정보를 삭제하는데 실패했습니다.")
