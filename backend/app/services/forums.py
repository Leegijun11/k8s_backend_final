#service_forums_create 게시물 생성
#service_forums_list 게시물 목록
#service_forums_context 게시물 상세
#service_forums_update 게시물 수정
#service_forums_delete 게시물 삭제

from fastapi import HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select

from app.db.scheme.forums import Forum_Create, Forum_Update
from app.db.crud.forums import Forums_CRUD
from app.db.crud.forumlikes import ForumLike

class Forum_Service:
    

    #게시물 작성
    @staticmethod
    async def service_forums_create(db: AsyncSession, forum_data:Forum_Create, u_id:int ):
        try:

            new_forum=await Forums_CRUD.crud_forum_create(db, forum_data=forum_data, u_id=u_id)
            return new_forum
        
        except HTTPException:
            raise
        except Exception as e:
            await db.rollback()
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"게시글 작성 실패"
            )


    #게시글 목록
    @staticmethod
    async def service_forums_list(db:AsyncSession,
                                  tag: str | None=None,
                                  baby_character: str | None=None,
                                  sort: str | None=None,
                                  u_id: int | None=None):
        try:
            formus=await Forums_CRUD.crud_forum_list(db, tag=tag, baby_character=baby_character, sort=sort, u_id=u_id)
            return formus
        except Exception as e:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"게시글 목록 조회 실패: {e}"
            )
    

    #게시글 상세 조회
    @staticmethod
    async def service_forums_context(db:AsyncSession, f_id:int, u_id: int | None = None):
        try:
            forum=await Forums_CRUD.crud_forum_context(db, f_id=f_id)

            if not forum:
                raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="해당 게시글을 찾을수 없음")
            
            if u_id:
                like_check=select(ForumLike).where(ForumLike.f_id==f_id, ForumLike.u_id == u_id)
                like_result=await db.execute(like_check)
                forum.is_liked=like_result.scalar_one_or_none() is not None
            else:
                forum.is_liked=False
            return forum
        
        except HTTPException:
            raise
        except Exception as e:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"게시글 상세 조회 실패: {e}"
            )  

    #게시글 수정
    @staticmethod
    async def service_forums_update(db: AsyncSession, f_id:int, forum_data: Forum_Update, u_id:int):
        try:
            forum=await Forums_CRUD.crud_forum_context(db, f_id=f_id)

            if not forum:
                raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="해당 게시물을 찾을수 없음")
            
            if forum.u_id != u_id:
                raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="게시글을 수정할 권한이 없음")
            
            updated_forum=await Forums_CRUD.crud_forum_update(db, db_forum=forum, forum_data=forum_data)
            return updated_forum
        
        except HTTPException:
            raise
        except Exception as e:
            await db.rollback()
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"게시글 수정 실패: {e}"
            )

    #게시글 삭제
    @staticmethod
    async def service_forums_delete(db: AsyncSession, f_id: int, u_id:int):
        try:
            forum=await Forums_CRUD.crud_forum_context(db, f_id=f_id)

            if not forum:
                raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="해당 게시물을 찾을수 없음")
            
            if forum.u_id != u_id:
                raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="게시글을 삭제할 권한이 없음")
            
            await Forums_CRUD.crud_forum_delete(db, db_forum=forum)
            return True
        
        except HTTPException:
            raise
        except Exception as e:
            await db.rollback()
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"게시글 삭제 실패: {e}"
            )