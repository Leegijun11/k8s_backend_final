#crud_forumlike_create 게시글 좋아요 생성
#crud_forumlike_count 게시글 목록
#crud_forumlike_delete 게시글 좋아요 취서


from sqlalchemy import select, func, desc
from sqlalchemy.orm import joinedload
from sqlalchemy.ext.asyncio import AsyncSession
from app.db.models.forumlikes import ForumLike
from app.db.models.forums import Forums


class ForumLikes_CRUD:

    #게시글 좋아요 생성
    @staticmethod
    async def crud_forumlike_create(db:AsyncSession, f_id:int, u_id:int):
        forum=select(ForumLike).where(ForumLike.f_id==f_id, ForumLike.u_id==u_id)
        result=await db.execute(forum)
        like_result=result.scalar_one_or_none()

        if like_result:
            return False
        
        new_like=ForumLike(f_id=f_id, u_id=u_id)
        db.add(new_like)

        forum_count=await db.get(Forums, f_id)
        if forum_count:
            forum_count.f_like_count += 1

        await db.commit()
        return True
    
 
    #게시글 좋아요 개수
    @staticmethod
    async def crud_forumlike_count(db:AsyncSession, f_id:int):
        forum=select(Forums.f_like_count).where(Forums.f_id == f_id)
        result=await db.execute(forum)
        count=result.scalar_one_or_none()

        return count if count is not None else 0
    
    
    #게시글 좋아요 취소
    @staticmethod
    async def crud_forumlike_delete(db:AsyncSession, f_id: int, u_id: int):
        forum=select(ForumLike).where(ForumLike.f_id==f_id, ForumLike.u_id==u_id)
        result=await db.execute(forum)
        like_delete=result.scalar_one_or_none()

        if not like_delete:
            return False
        
        await db.delete(like_delete)

        forum_count=await db.get(Forums, f_id)
        if forum_count and forum_count.f_like_count > 0:
            forum_count.f_like_count -= 1

        await db.commit()
        return True