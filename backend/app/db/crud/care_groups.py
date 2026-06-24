from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import func
from sqlalchemy.future import select
from datetime import datetime
from app.db.models.care_group import Care_Group 
from app.db.scheme.care_groups import CareGroup_Create


class CareGroup_Crud:
    # 그룹 등록
    @staticmethod
    async def crud_caregroups_create(db:AsyncSession,
                                     group: CareGroup_Create) -> Care_Group:          
        data = group.model_dump()
        db_data=Care_Group(**data)
        db.add(db_data)
        await db.flush()
        return db_data


    # 그룹 삭제
    @staticmethod
    async def crud_caregroups_del(db:AsyncSession,
                                  g_id:int) -> Care_Group | None:
        db_data = await db.get(Care_Group, g_id)
        if db_data:
            await db.delete(db_data)
            await db.flush()
            return db_data
        return None
  

