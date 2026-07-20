from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from datetime import date, datetime, timedelta
from sqlalchemy import select, exists

from app.db.models.diaries import Diary
from app.db.models.logs import Log
from app.db.models.babyimages import BabyImage
from app.db.models.babies import Baby
from app.db.models.parents import Parent


class Diary_Crud:

    # b_id, d_date로 logs 1행 가져오기
    @staticmethod
    async def crud_diaries_get_log(
        db: AsyncSession,
        b_id: int,
        d_date: date
    ) -> Log | None:

        start = datetime.combine(d_date, datetime.min.time())
        end = start + timedelta(days=1)

        result = await db.execute(
            select(Log).where(
                Log.b_id == b_id,
                Log.l_date >= start,
                Log.l_date < end
            )
        )

        return result.scalars().first()

    # b_id, d_date로 babyimages 여러 행 가져오기
    @staticmethod
    async def crud_diaries_get_images(
        db: AsyncSession,
        b_id: int,
        d_date: date
    ) -> list[BabyImage]:

        start = datetime.combine(d_date, datetime.min.time())
        end = start + timedelta(days=1)

        result = await db.execute(
            select(BabyImage).where(
                BabyImage.b_id == b_id,
                BabyImage.i_date >= start,
                BabyImage.i_date < end
            )
        )

        return result.scalars().all()

    # 일기 생성
    @staticmethod
    async def crud_diaries_create(
        db: AsyncSession,
        diary_data: dict
    ) -> Diary:

        db_data = Diary(**diary_data)
        db.add(db_data)
        await db.flush()
        return db_data

    # 날짜별 일기 목록 조회
    @staticmethod
    async def crud_diaries_list(
        db: AsyncSession,
        b_id: int,
        d_date: date
    ) -> list[Diary]:

        result = await db.execute(
            select(Diary).where(
                Diary.b_id == b_id,
                Diary.d_date == d_date
            )
        )

        return result.scalars().all()

    # 일기 상세 조회
    @staticmethod
    async def crud_diaries_detail(db: AsyncSession, d_id: int) -> Diary | None:
        result = await db.execute(select(Diary).where(Diary.d_id == d_id))

        return result.scalars().first()
    


    # baby의 그룹에 해당 유저가 속해있는지 확인해야함
    @staticmethod
    async def crud_check_diary_access(db: AsyncSession, b_id: int, u_id: int) -> bool:
        result = await db.execute(
            select(
                exists().where(
                    Baby.b_id == b_id,
                    Baby.g_id == Parent.g_id,
                    Parent.u_id == u_id,
                )
            )
        )
        return result.scalar()

    # 일기 수정
    @staticmethod
    async def crud_diaries_update(
        db: AsyncSession,
        d_id: int,
        update_data: dict
    ) -> Diary | None:

        db_data = await db.get(Diary, d_id)

        if db_data:
            for key, value in update_data.items():
                setattr(db_data, key, value)

            await db.flush()
            return db_data

        return None

    # 일기 삭제
    @staticmethod
    async def crud_diaries_del(
        db: AsyncSession,
        d_id: int
    ) -> Diary | None:

        db_data = await db.get(Diary, d_id)

        if db_data:
            await db.delete(db_data)
            await db.flush()
            return db_data

        return None