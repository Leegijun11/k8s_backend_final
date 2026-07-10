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
from app.db.models.babies import Baby
from app.db.models.babycharacters import BabyCharacter
from app.db.crud.babies import Baby_Crud



CHARACTER_MAP = {
        "curiosity": "c_curiosity",
        "active": "c_active",
        "shy": "c_shy",
        "eater": "c_eater",
        "sleepy": "c_sleepy",
        "charm": "c_charm"
    }
class Forum_Service:
    
    #게시물 작성
    @staticmethod
    async def service_forums_create(db: AsyncSession, forum_data: Forum_Create, u_id: int):
        try:
            if forum_data.b_id is None:
                babies = await Baby_Crud.crud_babies_list(db, u_id)
                if babies and len(babies) > 0:
                    forum_data.b_id = babies[0].b_id
            
            new_forum = await Forums_CRUD.crud_forum_create(db, forum_data=forum_data, u_id=u_id)
            return new_forum
        
        except HTTPException:
            raise
        except Exception as e:
            await db.rollback()
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"게시글 작성 실패: {str(e)}"
            )

    #게시물 목록
    @staticmethod
    async def service_forums_list(db: AsyncSession,
                                  tag: str | None = None,
                                  baby_character: str | list | None = None,
                                  sort: str | None = None,
                                  u_id: int | None = None,
                                  b_id: int | None = None):
        try:
            if baby_character == "my_baby":
                if not u_id:
                    raise HTTPException(status_code=400, detail="로그인이 필요합니다.")
                
                if b_id:
                    target_id = b_id
                else:
                    babies = await Baby_Crud.crud_babies_list(db, u_id)
                    if not babies:
                        raise HTTPException(status_code=400, detail="등록된 아기 정보가 없습니다.")
                    target_id = babies[0].b_id
                
                stmt = select(BabyCharacter).where(BabyCharacter.b_id == target_id)
                result = await db.execute(stmt)
                my_baby_char = result.scalar_one_or_none()
                
                if not my_baby_char:
                    raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="아기의 성격이 아직 등록 되지 않았습니다")

                active_chars = [key for key, field_name in CHARACTER_MAP.items() 
                                if getattr(my_baby_char, field_name)]
                
                if not active_chars:
                    raise HTTPException(status_code=400, detail="아기의 성격이 하나도 등록되지 않았습니다")
                
                baby_character = active_chars

            forums = await Forums_CRUD.crud_forum_list(
                db, tag=tag, baby_character=baby_character, sort=sort, u_id=u_id
            )
            return forums

        except HTTPException:
            raise
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