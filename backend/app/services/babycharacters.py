from sqlalchemy.ext.asyncio import AsyncSession
from fastapi import HTTPException
from app.db.crud.babycharacters import BabyCharacter_Crud
from app.db.scheme.babycharacters import BabyCharacter_Create, BabyCharacter_Update


class BabyCharacterService:

    # 아이 정보 등록
    @staticmethod
    async def service_babycharacter_create(baby:BabyCharacter_Create, db:AsyncSession):
        try:
            db_data=await BabyCharacter_Crud.crud_babycharacters_create(baby, db)
            return db_data
        except Exception as e:
            raise HTTPException(status_code=400, detail="아이 성격 정보 등록에 실패했습니다.")
        
    # 아이 세부 정보
    @staticmethod
    async def service_babycharacter_read(c_id:int, db:AsyncSession):
        try:
            db_data=await BabyCharacter_Crud.crud_babycharacters_detail(c_id, db)
            if db_data is None:
                raise HTTPException(status_code=400, detail="아이의 성격 정보를 불러오는데 실패했습니다.")
            return db_data
        except Exception as e:
            raise HTTPException(status_code=400, detail="아이의 성격 정보를 불러오는데 실패했습니다.")
        
    # 아이 정보 수정
    @staticmethod
    async def service_babycharacter_update(c_id:int, baby:BabyCharacter_Update, db: AsyncSession):
        try:
            exist_babycharacter=await BabyCharacter_Crud.crud_babycharacters_detail(c_id, db)
            if exist_babycharacter is None:
                raise HTTPException(status_code=400, detail="아이의 성격 정보를 수정하는데 실패했습니다.")
            db_data=await BabyCharacter_Crud.crud_babycharacters_update(c_id, baby, db)
            return db_data
        except Exception as e:
            raise HTTPException(status_code=400, detail="아이의 성격 정보를 수정하는데 실패했습니다.")
    