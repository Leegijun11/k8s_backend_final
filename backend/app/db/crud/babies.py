from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from app.db.models.babies import Baby 
from app.db.models.care_group import Care_Group
from app.db.scheme.babies import Baby_Create, Baby_Update


class Baby_Crud:
    # 아이 정보 등록
    @staticmethod
    async def crud_babies_create(db:AsyncSession, 
                                 baby_dict: dict) -> Baby:          
        db_data = Baby(**baby_dict)
        db.add(db_data)
        await db.flush()
        return db_data


    # 아이 목록
    @staticmethod
    async def crud_babies_list(db:AsyncSession,
                               u_id:int) -> list[Baby]:
        result = await db.execute(select(Baby)
                                  .join(Care_Group, Baby.g_id == Care_Group.g_id)
                                  .filter(Care_Group.creator_id == u_id))
        return result.scalars().all()


    # 아이 세부 정보
    @staticmethod
    async def crud_babies_detail(db:AsyncSession, 
                           b_id:int) -> Baby | None:
        result = await db.execute(select(Baby).filter(Baby.b_id == b_id))
        return result.scalars().first()


    # 아이 정보 수정
    @staticmethod
    async def crud_babies_update(db:AsyncSession, 
                               b_id:int, 
                               baby:Baby_Update) -> Baby | None:
        db_data=await db.get(Baby, b_id)
        
        if db_data:           
            update_data= baby.model_dump(exclude_unset=True)

            for key, value in update_data.items():
                setattr(db_data, key, value)

            await db.flush()
            return db_data
            
        return None
    

    # 아이 정보 삭제
    @staticmethod
    async def crud_babies_del(db:AsyncSession, 
                               b_id:int) -> Baby | None:
        db_data = await db.get(Baby, b_id)
        if db_data:
            await db.delete(db_data)
            await db.flush()
            return db_data
        return None
  
