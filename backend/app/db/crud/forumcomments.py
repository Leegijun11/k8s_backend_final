from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from typing import Optional
from app.db.models.forumcomments import ForumComment
from app.db.scheme.forumcomments import ForumComment_Create, ForumComment_Update

class ForumComment_Crud:

    # 1. 댓글 추가
    @staticmethod
    async def crud_forumcomments_create(db:AsyncSession, comment:ForumComment_Create) -> ForumComment:
        data = comment.model_dump()
        db_data=ForumComment(**data)
        db.add(db_data)
        await db.flush()
        return db_data
    
    # 2. 댓글 조회
    @staticmethod
    async def crud_forumcomments_list(db:AsyncSession, f_id:int) -> list[ForumComment]:
        result=await db.execute(select(ForumComment)
                                .filter(ForumComment.f_id == f_id)
                                .order_by(ForumComment.fc_id.asc()))
        return result.scalars().all()

    # 3. 댓글 수정
    @staticmethod
    async def crud_forumcomments_update(db:AsyncSession, fc_id:int, comment:ForumComment_Update) -> ForumComment | None:
        db_data=await db.get(ForumComment, fc_id)
        if db_data:
            update_data=comment.model_dump(exclude_unset=True)

            for key, value in update_data.items():
                setattr(db_data, key, value)

            await db.flush()
            return db_data
            
        return None
    
    # 4. 댓글 삭제
    @staticmethod
    async def crud_forumcomment_del(db:AsyncSession, fc_id:int) -> ForumComment | None:
        db_data=await db.get(ForumComment, fc_id)
        if db_data:
            await db.delete(db_data)
            await db.flush()
            return db_data
        return None
