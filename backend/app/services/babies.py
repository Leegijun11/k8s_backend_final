from sqlalchemy.ext.asyncio import AsyncSession
from app.db.scheme.babies import Baby_Create, Baby_Update
from app.db.crud.babies import Baby_Crud
from fastapi import HTTPException

class BabyService:

    # 1. 아이 정보 등록
    @staticmethod
    async def service_babies_create(baby:Baby_Create, db: AsyncSession):
        if baby.b_height <= 0 or baby.b_weight <= 0:
            raise HTTPException(status_code=400, detail="아이 정보 등록에 실패했습니다.")
        try:
            db_data=await Baby_Crud.crud_babies_create(baby, db)
            return db_data
        except Exception as e:
            raise HTTPException(status_code=400, detail="아이 정보 등록에 실패했습니다.")

    # 2. 아이 목록 조회
    @staticmethod
    async def service_babies_list(g_id:int, db:AsyncSession):
        try:
            db_data=await Baby_Crud.crud_babies_list(g_id, db)
            if db_data is None:
                raise HTTPException(status_code=400, detail="아이들의 정보를 불러오는데 실패했습니다.")
            return db_data
        except Exception as e:
            raise HTTPException(status_code=400, detail="아이들의 정보를 불러오는데 실패했습니다.")

        
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
        

    # 4. 아이 정보 수정
    @staticmethod
    async def service_babies_update(b_id:int, baby:Baby_Update, db: AsyncSession):
        if (baby.b_height is not None and baby.b_height <= 0) or \
           (baby.b_weight is not None and baby.b_weight <= 0):
           raise HTTPException(status_code=400, detail="키와 몸무게는 0보다 커야 합니다.")
        try:
            exist_baby=await Baby_Crud.crud_babies_detail(b_id, db)
            if exist_baby is None:
                raise HTTPException(status_code=400, detail="아이의 정보를 수정하는데 실패했습니다.")
            db_data=await Baby_Crud.crud_babies_update(b_id, baby, db)
            return db_data
        except Exception as e:
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
