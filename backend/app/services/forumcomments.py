from sqlalchemy.ext.asyncio import AsyncSession
from app.db.scheme.forumcomments import ForumComment_Create, ForumComment_Update
from app.db.crud.forumcomments import ForumComment_Crud
from fastapi import HTTPException, status
from sqlalchemy.future import select
from sqlalchemy.orm import joinedload
from app.db.models.forumcomments import ForumComment

class ForumCommentService:
    
    # 1. 댓글 등록
    @staticmethod
    async def service_forumcomments_create(db:AsyncSession,f_id:int, u_id:int, comment:ForumComment_Create):
        if not comment.fc_content.strip():
            raise HTTPException(status_code=400, detail="댓글 내용은 공백일 수 없습니다.")
        try:
            db_data=await ForumComment_Crud.crud_forumcomments_create(db,f_id, u_id, comment)
            await db.commit()
        
            db_data = await db.scalar(select(ForumComment).options(joinedload(ForumComment.user)).where(ForumComment.fc_id == db_data.fc_id))
            
            return db_data
        except Exception as e:
            await db.rollback()
            raise HTTPException(status_code=500, detail=f"댓글 등록에 실패했습니다 : {e}")
        

# 2. 댓글 조회
    @staticmethod
    async def service_forumcomments_list(db: AsyncSession, f_id: int, u_id: int):
        try:
            db_data = await ForumComment_Crud.crud_forumcomments_list(db, f_id)
            
            for comment in db_data:
                comment.is_liked = any(like.u_id == u_id for like in comment.comment_likes)
                
            return db_data
        except Exception as e:
            await db.rollback()
            raise HTTPException(status_code=500, detail=f"댓글 조회에 실패했습니다 : {e}")
        


    # 3. 댓글 수정
    @staticmethod
    async def service_forumcomments_update(db:AsyncSession, fc_id:int, u_id:int, comment:ForumComment_Update):
        if comment.fc_content is not None and not comment.fc_content.strip():
            raise HTTPException(status_code=400, detail="댓글 내용은 공백일 수 없습니다.")
        try:
            db_data=await ForumComment_Crud.crud_forumcomments_update(db, fc_id,u_id, comment)
            if db_data is None:
                raise HTTPException(status_code=404, detail="댓글을 찾을 수 없습니다.")
            await db.commit()
            
            db_data = await db.scalar(select(ForumComment).options(joinedload(ForumComment.user)).where(ForumComment.fc_id == fc_id))
            
            return db_data
        except HTTPException:
            await db.rollback()
            raise
        except Exception as e:
            await db.rollback()
            raise HTTPException(status_code=500, detail=f"댓글 수정에 실패했습니다 : {e}")
        

    # 4. 댓글 삭제
    @staticmethod
    async def service_forumcomments_delete(db:AsyncSession, fc_id:int, u_id: int):
        try:
            db_data=await ForumComment_Crud.crud_forumcomment_del(db, fc_id, u_id)
            if not db_data:
                raise HTTPException(status_code=404, detail="댓글이 존재하지 않습니다.")
            await db.commit()
            return {"message" : "댓글 삭제 성공"}
        except HTTPException:
            await db.rollback()
            raise
        except Exception as e:
            await db.rollback()
            raise HTTPException(status_code=500, detail=f"댓글 삭제에 실패했습니다 : {e}")
        