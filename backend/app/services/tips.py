#service_tips_list 팁 목록
#service_tips_info 팁 상세 내용

from pydantic import BaseModel, Field, EmailStr, ConfigDict
from fastapi import status, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from typing import Optional
from app.db.crud.tips import Tip_Crud, Tip


class Tip_Service:


    #팁 목록
    @staticmethod
    async def service_tip_list(db:AsyncSession, t_age:Optional[int]=None, skip:int=0, limit:int=10):
        try:
            tips=await Tip_Crud.crud_tips_list(db, t_age=t_age, skip=skip, limit=limit)

            if not tips:
                raise HTTPException(
                    status_code=status.HTTP_404_NOT_FOUND,
                    detail="TIP 정보들을 불러오는데 실패했습니다"
                )
            return tips
        
        except HTTPException:
            raise
        except Exception as e:
            raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                                detail=f"팁 목록 중 서버 에러 발생")
        
    #팁 상세 내용
    @staticmethod
    async def service_tips_info(db:AsyncSession, t_id:int):
        try:
            tip=await Tip_Crud.crud_tips_by_t_id(db, t_id=t_id)

            if not tip:
                raise HTTPException(
                    status_code=status.HTTP_404_NOT_FOUND,
                    detail="TIP 정보들을 불러오는데 실패했습니다"
                )
            return tip
        
        except HTTPException:
            raise
        except Exception as e:
            raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                                detail=f"팁 상세 내용 조회 중 서버 에러 발생")