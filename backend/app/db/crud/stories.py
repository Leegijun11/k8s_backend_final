from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from datetime import date
from app.db.models.stories import Story
from app.db.models.diaries import Diary


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