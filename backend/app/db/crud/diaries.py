from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import func
from sqlalchemy.future import select
from datetime import datetime
from app.db.models.diaries import Diary 
from app.db.scheme.diaries import Diary_Create, Diary_Update


class Diary_Crud:
    # 일기 등록
    @staticmethod
    async def crud_diaries_create(db:AsyncSession,
                                  diary: Diary_Create) -> Diary:          
        data = diary.model_dump()
        db_data=Diary(**data)
        db.add(db_data)
        await db.flush()
        return db_data


    # 일기 목록
    @staticmethod
    async def crud_diaries_list(db:AsyncSession,
                                d_date:datetime) -> list[Diary] | None:
        result = await db.execute(select(Diary)
                                  .where(func.date(Diary.d_date) == func.date(d_date)))
        return list(result.scalars().all())


    # 일기 상세
    @staticmethod
    async def crud_diaries_detail(db:AsyncSession,
                                   d_id:int) -> Diary | None:
        result = await db.execute(select(Diary).where(Diary.d_id == d_id))
        return result.scalars().one_or_none()


    # 일기 삭제
    @staticmethod
    async def crud_diaries_del(db:AsyncSession, 
                               d_id:int) -> Diary | None:
        db_data = await db.get(Diary, d_id)
        if db_data:
            await db.delete(db_data)
            await db.flush()
            return db_data
        return None
  

