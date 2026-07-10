#service_forumcommentlikes_create: 게시글 댓글 좋아요 생성
#service_forumcommentlikes_delete: 게시글 댓글 좋아요 취소
#service_forumcommentlikes_count: 게시글 댓글 좋아요 개수




from sqlalchemy.ext.asyncio import AsyncSession
from fastapi import HTTPException, status
from app.db.crud.forumcommentlikes import ForumCommentLikes_CRUD

class ForumCommentLikesService:

    #댓글 좋아요 추가
    @staticmethod
    async def service_forumcommentlikes_create(db: AsyncSession, fc_id:int, u_id:int):
        try:
            create=await ForumCommentLikes_CRUD.crud_forumcommentlikes_create(db, fc_id, u_id)

            if not create:
                raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="이미 좋아요를 누르습니다")
            
            await db.commit()
            return {"msg":"좋아요 성공"}
        
        except HTTPException:
            raise
        except Exception as e:
            raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                                detail=f"댓글 좋아요 생성 실패: {e}")
        

    #댓글 좋아요 취서
    @staticmethod
    async def service_forumcommentlikes_delete(db: AsyncSession, fc_id:int, u_id:int):
        try:
            delete=await ForumCommentLikes_CRUD.crud_forumcommentlikes_delete(db, fc_id, u_id)

            if not delete:
                raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, 
                                    detail="좋아요 기록이 존재하지 않거나 권한이 없습니다")
            await db.commit()
            return {"msg":"좋아요가 취소되었습니다"}
        
        except HTTPException:
            raise
        except Exception as e:
            raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                                detail=f"댓글 좋아요 취소 실패: {e}")
        

    #댓글 좋아요 개수
    @staticmethod
    async def service_forumcommentlikes_count(db: AsyncSession, fc_id:int):
        try:
            count=await ForumCommentLikes_CRUD.crud_forumcommentlike_count(db, fc_id)

            return {"count": count}
        
        except HTTPException:
            raise
        except Exception as e:
            raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                                detail=f"댓글 좋아요 개수 조회 실패: {e}")