#crud_direct_diaries_create: 직접 일기 생성

from sqlalchemy import select, func, desc, or_
from sqlalchemy.orm import joinedload, selectinload
from sqlalchemy.ext.asyncio import AsyncSession

from app.db.models.diaries import Diary
from app.db.scheme.diaries import Diary_Create


class Direct_Diaries_CRUD:

    #직접 일기 생성
    @staticmethod
    async def crud_direct_diaries_create(db:AsyncSession, diary_create:Diary_Create):
        diary_data=diary_create.model_dump(exclude_unset=True)
        new_diary=Diary(**diary_data)

        db.add(new_diary)
        await db.commit()
        await db.refresh(new_diary)

        return new_diary