from sqlalchemy.ext.asyncio import AsyncSession
from fastapi import HTTPException
from app.db.crud.babycharacters import BabyCharacter_Crud
from app.db.scheme.babycharacters import BabyCharacter_Create, BabyCharacter_Update


class BabyCharacterService:

    # 아이 성격 정보 등록
    @staticmethod
    async def service_babycharacter_create(baby:BabyCharacter_Create, db:AsyncSession):
        try:
            db_data=await BabyCharacter_Crud.crud_babycharacters_create(db, baby)
            await db.commit()
            await db.refresh(db_data)
            return db_data
        
        except Exception as e:
            await db.rollback()
            raise HTTPException(status_code=400, detail="아이 성격 정보 등록에 실패했습니다.")
        
    # 아이 성격세부 정보
    @staticmethod
    async def service_babycharacter_read(c_id:int, db:AsyncSession):
        try:
            db_data=await BabyCharacter_Crud.crud_babycharacters_detail(db, c_id)
        except Exception as e:
            raise HTTPException(status_code=500, detail="아이의 성격 정보를 불러오는 중 오류가 발생했습니다.")
        
        if db_data is None:
                raise HTTPException(status_code=404, detail="해당 아이 성격 정보를 찾을 수 없습니다.")
        return db_data
        
    # 아이 성격 정보 수정
    @staticmethod
    async def service_babycharacter_update(c_id:int, baby:BabyCharacter_Update, db: AsyncSession):
        try:
            exist_babycharacter=await BabyCharacter_Crud.crud_babycharacters_detail(db, c_id)
        except Exception as e:
            raise HTTPException(status_code=500, detail="아이의 성격 정보를 조회하는 중 오류가 발생했습니다.")
        if exist_babycharacter is None:
            raise HTTPException(status_code=404, detail="수정할 아이의 성격 정보가 존재하지 않습니다.")
        
        try:
            db_data=await BabyCharacter_Crud.crud_babycharacters_update(db, c_id, baby)
            await db.commit()
            await db.refresh(db_data)
            return db_data
        except Exception as e:
            await db.rollback()
            raise HTTPException(status_code=404, detail="아이의 성격 정보를 수정하는데 실패했습니다.")
    