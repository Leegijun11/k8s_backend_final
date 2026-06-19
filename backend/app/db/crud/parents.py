from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select

from app.db.models.parents import Parent 
from app.db.scheme.parents import Parent_Create, Parent_Update

from app.db.models.care_group import Care_Group


class Parent_Crud:
    # 양육자 등록
    @staticmethod
    async def crud_parents_create(db:AsyncSession, 
                               parent: Parent_Create) -> Parent:          
        data = parent.model_dump()
        db_data=Parent(**data)
        db.add(db_data)
        await db.flush()
        return db_data


    # 양육자 그룹주 확인
    @staticmethod
    async def crud_parents_group(db:AsyncSession, 
                                 u_id:int) -> Care_Group | None:
        result = await db.execute(select(Care_Group)
                                  .filter(Care_Group.creator_id == u_id))
        return result.scalars().first()
    

    # 양육자 목록
    @staticmethod
    async def crud_parents_list(db:AsyncSession, 
                                g_id:int) -> list[Parent]:
        result = await db.execute(select(Parent)
                                  .filter(Parent.g_id == g_id))
        return list(result.scalars().all())
    

    # 양육자 아기 선택 업데이트
    @staticmethod
    async def crud_parents_update(db:AsyncSession, 
                               p_id:int, 
                               parent:Parent_Update) -> Parent | None:
        db_data=await db.get(Parent, p_id)
        
        if db_data:             
            update_data= parent.model_dump(exclude_unset=True)
            for key, value in update_data.items():
                setattr(db_data, key, value)

            await db.flush()
            return db_data
            
        return None


    # 양육자 삭제
    @staticmethod
    async def crud_parents_del(db:AsyncSession, 
                               p_id:int) -> Parent | None:
        db_data = await db.get(Parent, p_id)
        if db_data:
            await db.delete(db_data)
            await db.flush()
            return db_data
        return None
    
    