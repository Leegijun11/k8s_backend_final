#crud_forumcommentlikes_create: 게시글 댓글 좋아요 생성
#crud_forumcommentlikes_delete: 게시글 댓글 좋아요 취소
#crud_forumcommentlikes_count: 게시글 댓글 좋아요 개수


from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func
from app.db.models.forumcommentlikes import ForumCommentLike
from app.db.models.forumcomments import ForumComment

class ForumCommentLikes_CRUD:


    #댓글 좋아요 생성
    @staticmethod
    async def crud_forumcommentlikes_create(db: AsyncSession, fc_id:int, u_id:int):
        comment_like=select(ForumCommentLike).where(ForumCommentLike.fc_id==fc_id,
                                                    ForumCommentLike.u_id==u_id)
        result=await db.execute(comment_like)
        cl_data=result.scalar_one_or_none()

        if cl_data:
            return False
        
        new_like=ForumCommentLike(fc_id=fc_id, u_id=u_id)
        db.add(new_like)

        like_count=await db.get(ForumComment, fc_id)
        if like_count and hasattr(like_count, 'fc_like_count'):
            like_count.fc_like_count += 1

        await db.flush()
        return True
    

    #댓글 좋아요 취소
    @staticmethod
    async def crud_forumcommentlikes_delete(db:AsyncSession, fc_id:int, u_id:int):
        # 에러 확인용
        # print(f"DEBUGGING -> fc_id: {fc_id} (타입: {type(fc_id)}), u_id: {u_id} (타입: {type(u_id)})")


        comment_like=select(ForumCommentLike).where(ForumCommentLike.fc_id==fc_id,
                                                    ForumCommentLike.u_id==u_id)
        result=await db.execute(comment_like)
        delete_like=result.scalar_one_or_none()

        if not delete_like:
            return False
        
        await db.delete(delete_like)

        like_count=await db.get(ForumComment, fc_id)
        if like_count and hasattr(like_count, 'fc_like_count') and like_count.fc_like_count > 0:
            like_count.fc_like_count -= 1

        await db.flush()
        return True
    
    #게시물 좋아요 개수
    @staticmethod
    async def crud_forumcommentlike_count(db: AsyncSession, fc_id:int):

        stmt=select(func.count(ForumCommentLike.fc_l_id)).where(ForumCommentLike.fc_id==fc_id)
        result=await db.execute(stmt)
        count=result.scalar()

        return count if count is not None else 0
        