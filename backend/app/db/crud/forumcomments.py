from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from sqlalchemy.orm import joinedload, selectinload
from typing import Optional
from app.db.models.forumcomments import ForumComment
from app.db.scheme.forumcomments import ForumComment_Create, ForumComment_Update

class ForumComment_Crud:

    # 1. 댓글 추가
    @staticmethod
    async def crud_forumcomments_create(db:AsyncSession, f_id:int, u_id: int, comment:ForumComment_Create) -> ForumComment:
        data = comment.model_dump(exclude={"f_id","u_id"})
        db_data=ForumComment(f_id=f_id, u_id=u_id, **data)

        db.add(db_data)
        await db.flush()
        return await db.scalar(select(ForumComment).options(joinedload(ForumComment.user)).where(ForumComment.fc_id == db_data.fc_id))
    
    # 2. 댓글 조회
    @staticmethod
    async def crud_forumcomments_list(db: AsyncSession, f_id: int) -> list[ForumComment]:
        comment = (select(ForumComment).options(joinedload(ForumComment.user),
                                                selectinload(ForumComment.comment_likes))
                                                .where(ForumComment.f_id == f_id)
                                                .order_by(ForumComment.fc_id.asc()))
        result = await db.execute(comment)
        return list(result.scalars().all())

    # 3. 댓글 수정
    @staticmethod
    async def crud_forumcomments_update(db:AsyncSession, fc_id:int, u_id:int, comment:ForumComment_Update) -> ForumComment | None:

        stmt=select(ForumComment).where(ForumComment.fc_id==fc_id, ForumComment.u_id == u_id)
        result=await db.execute(stmt)
        db_data=result.scalars().first()

        if db_data:
            update_data=comment.model_dump(exclude_unset=True, exclude={"u_id", "f_id", "fc_id"})

            for key, value in update_data.items():
                setattr(db_data, key, value)

            await db.flush()
            return db_data
            
        return None
    
    # 4. 댓글 삭제
    @staticmethod
    async def crud_forumcomment_del(db:AsyncSession, fc_id:int, u_id: int) -> ForumComment | None:

        stmt=select(ForumComment).where(ForumComment.fc_id==fc_id, ForumComment.u_id == u_id)
        result=await db.execute(stmt)
        db_data=result.scalars().first()

        if db_data:
            await db.delete(db_data)
            await db.flush()
            return db_data
        return None
