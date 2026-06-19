from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from app.db.models.babycharacters import BabyCharacter 
from app.db.scheme.babycharacters import BabyCharacter_Create, BabyCharacter_Update


class BabyCharacter_Crud:
    # 아이 캐릭터 정보 등록
    @staticmethod
    async def crud_babycharacters_create(db:AsyncSession, 
                                 character: BabyCharacter_Create) -> BabyCharacter:          
        data = character.model_dump()
        db_data=BabyCharacter(**data)
        db.add(db_data)
        await db.flush()
        return db_data


    # 아이 캐릭터 정보
    @staticmethod
    async def crud_babycharacters_detail(db:AsyncSession,
                                         c_id:int) -> BabyCharacter | None:
        result = await db.execute(select(BabyCharacter).filter(BabyCharacter.c_id == c_id))
        return result.scalars().first()


    # 아이 캐릭터 정보 수정
    @staticmethod
    async def crud_babycharacters_update(db:AsyncSession,
                                         c_id:int,
                                         character:BabyCharacter_Update) -> BabyCharacter | None:
        db_data=await db.get(BabyCharacter, c_id)
        
        if db_data:           
            update_data= character.model_dump(exclude_unset=True)

            for key, value in update_data.items():
                setattr(db_data, key, value)

            await db.flush()
            return db_data
            
        return None

