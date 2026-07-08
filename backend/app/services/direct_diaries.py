#service_direct_diaries_create 직접 일기 생성

from fastapi import status, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession

from app.db.scheme.diaries import Diary_Create
from app.db.crud.direct_diaries import Direct_Diaries_CRUD
from datetime import date


class Direct_Diaries_Service:
    
    #직접 일기 생성
    @staticmethod
    async def service_direct_diaries_create(db: AsyncSession, diary_create:Diary_Create):
        try:
            new_diary=await Direct_Diaries_CRUD.crud_direct_diaries_create(db=db, diary_create=diary_create)

            return new_diary
        
        except HTTPException:
            raise
        except Exception as e:
            await db.rollback()
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=f"직접 일기 생성 실패{e}")
