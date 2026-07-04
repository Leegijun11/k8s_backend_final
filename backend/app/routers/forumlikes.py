#router_forumlikes_create 게시글 좋아요 생성
#router_forumlikes_delete 게시글 좋아요 취소


from fastapi import APIRouter, Depends, status
from sqlalchemy.ext.asyncio import AsyncSession
from app.db.database import get_db
from app.services.forumlikes import ForumLikes_Service
from app.core.auth import auth_get_u_id

router=APIRouter(prefix="/forumlike", tags=["ForumLike"])

#게시글 좋아요 생성
@router.post("/{f_id}")
async def router_forumlikes_create(f_id: int,
                                   u_id: int=Depends(auth_get_u_id),
                                   db: AsyncSession=Depends(get_db)):
    return await ForumLikes_Service.service_forumlikes_create(db, f_id=f_id, u_id=u_id)


#게시글 좋아요 취소
@router.delete("/{f_id}")
async def router_forumlikes_delete(f_id: int,
                                   u_id: int=Depends(auth_get_u_id),
                                   db: AsyncSession=Depends(get_db)):
    return await ForumLikes_Service.service_forumlike_delete(db, f_id=f_id, u_id=u_id)