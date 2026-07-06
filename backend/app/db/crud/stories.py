from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from datetime import date
from app.db.models.stories import Story
from app.db.models.diaries import Diary
from app.db.scheme.stories import Story_Update


class Story_Crud:

    # 기간 내 일기 목록 조회 (날짜순 정렬)
    @staticmethod
    async def crud_stories_get_diaries(db: AsyncSession, b_id: int, start_date: date, end_date: date) -> list[Diary]:
        result = await db.execute(
            select(Diary)
            .filter(Diary.b_id == b_id, Diary.d_date >= start_date, Diary.d_date <= end_date)
            .order_by(Diary.d_date.asc())
        )
        return result.scalars().all()

    # 디지털북 생성(insert)
    @staticmethod
    async def crud_stories_create(db: AsyncSession, story_data: dict) -> Story:
        db_data = Story(**story_data)
        db.add(db_data)
        await db.flush()
        return db_data

    # b_id 기준 디지털북 목록 조회
    @staticmethod
    async def crud_stories_list(db: AsyncSession, b_id: int) -> list[Story]:
        result = await db.execute(
            select(Story).filter(Story.b_id == b_id)
        )
        return result.scalars().all()

    # 디지털북 상세 조회
    @staticmethod
    async def crud_stories_detail(db: AsyncSession, s_id: int) -> Story | None:
        result = await db.execute(
            select(Story).filter(Story.s_id == s_id)
        )
        return result.scalars().first()
    

    # 디지털북 정보 수정
    @staticmethod
    async def crud_stories_update(db:AsyncSession,
                                  s_id:int,
                                  data:Story_Update) -> Story | None:
        db_data=await db.get(Story, s_id)
        
        if db_data:           
            update_data= data.model_dump(exclude_unset=True)

            for key, value in update_data.items():
                setattr(db_data, key, value)

            await db.flush()
            return db_data
            
        return None


    # 디지털북 삭제
    @staticmethod
    async def crud_stories_del(db: AsyncSession, s_id: int) -> Story | None:
        db_data = await db.get(Story, s_id)
        if db_data:
            await db.delete(db_data)
            await db.flush()
            return db_data
        return None