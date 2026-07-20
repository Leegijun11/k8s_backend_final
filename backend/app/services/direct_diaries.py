#service_direct_diaries_create 직접 일기 생성

from fastapi import status, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession

from app.db.scheme.diaries import Diary_Create
from app.db.crud.direct_diaries import Direct_Diaries_CRUD
from app.db.crud.diaries import Diary_Crud
from datetime import date


class Direct_Diaries_Service:
    
    #직접 일기 생성
    @staticmethod
    async def service_direct_diaries_create(db: AsyncSession, diary_create: Diary_Create, u_id: int):
        try:
            # ★ 추가: 이 b_id가 로그인한 u_id의 그룹 아기인지 확인
            has_access = await Diary_Crud.crud_check_diary_access(db, diary_create.b_id, u_id)
            if not has_access:
                raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="일기를 작성할 권한이 없습니다")

            new_diary = await Direct_Diaries_CRUD.crud_direct_diaries_create(db=db, diary_create=diary_create)

            return new_diary
        
        except HTTPException:
            await db.rollback()
            raise
        except Exception as e:
            await db.rollback()
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=f"직접 일기 생성 실패{e}")