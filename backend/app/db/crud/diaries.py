from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from datetime import date
from app.db.models.diaries import Diary
from app.db.models.logs import Log
from app.db.models.babyimages import BabyImage


class Diary_Crud:

    # b_id, d_date로 logs 1행 가져오기
    @staticmethod
    async def crud_diaries_get_log(db: AsyncSession, b_id: int, d_date: date) -> Log | None:
        result = await db.execute(
            select(Log).filter(Log.b_id == b_id, Log.l_date == d_date)
        )
        return result.scalars().first()

    # b_id, d_date로 babyimages 여러행 가져오기
    @staticmethod
    async def crud_diaries_get_images(db: AsyncSession, b_id: int, d_date: date) -> list[BabyImage]:
        result = await db.execute(
            select(BabyImage).filter(BabyImage.b_id == b_id, BabyImage.i_date == d_date)
        )
        return result.scalars().all()

    # 일기 생성(insert)
    @staticmethod
    async def crud_diaries_create(db: AsyncSession, diary_data: dict) -> Diary:
        db_data = Diary(**diary_data)
        db.add(db_data)
        await db.flush()
        return db_data
    

    # 날짜별 일기 목록 조회
    @staticmethod
    async def crud_diaries_list(db: AsyncSession, b_id: int, d_date: date) -> list[Diary]:
        result = await db.execute(
            select(Diary).filter(Diary.b_id == b_id, Diary.d_date == d_date)
        )
        return result.scalars().all()
    
    # 일기 상세 조회
    @staticmethod
    async def crud_diaries_detail(db: AsyncSession, d_id: int) -> Diary | None:
        result = await db.execute(
            select(Diary).filter(Diary.d_id == d_id)
        )
        return result.scalars().first()
    
    # 일기 수정
    @staticmethod
    async def crud_diaries_update(db: AsyncSession, d_id: int, update_data: dict) -> Diary | None:
        db_data = await db.get(Diary, d_id)

        if db_data:
            for key, value in update_data.items():
                setattr(db_data, key, value)

            await db.flush()
            return db_data

        return None
    
    # 일기 삭제
    @staticmethod
    async def crud_diaries_del(db: AsyncSession, d_id: int) -> Diary | None:
        db_data = await db.get(Diary, d_id)
        if db_data:
            await db.delete(db_data)
            await db.flush()
            return db_data
        return None