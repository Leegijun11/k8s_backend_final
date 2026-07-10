#service_forumlikes_create 게시물 생성
#service_forumlikes_delete 게시물 취소

from fastapi import HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from app.db.crud.forumlikes import ForumLikes_CRUD

class ForumLikes_Service:

    #좋아요 생성
    @staticmethod
    async def service_forumlikes_create(db: AsyncSession, f_id: int, u_id:int):
        try:
            liked=await ForumLikes_CRUD.crud_forumlike_create(db, f_id, u_id)
            if not liked:
                raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST,detail="이미 좋아요를 누른 게시글")
            return {"msg":"좋아요를 눌렀습니다"}
        
        except HTTPException:
            raise
        except Exception as e:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"좋아요 생성 실패: {e}"
            )
    

    #좋아요 취소
    @staticmethod
    async def service_forumlike_delete(db: AsyncSession, f_id: int, u_id: int):
        try:
            success = await ForumLikes_CRUD.crud_forumlike_delete(db, f_id=f_id, u_id=u_id)
            if not success:
                raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST,detail="좋아요를 누르지 않은 게시글")
            return {"msg": "좋아요를 취소했습니다."}

        except HTTPException:
            raise
        except Exception as e:
            await db.rollback()
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"좋아요 취소 실패: {e}"
            )
