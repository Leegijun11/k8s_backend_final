#router_forumcommentlikes_create: 게시글 댓글 좋아요 생성
#router_forumcommentlikes_delete: 게시글 댓글 좋아요 취소
#router_forumcommentlikes_count: 게시글 댓글 좋아요 개수

from fastapi import APIRouter, Depends, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.db.database import get_db
from app.core.auth import auth_get_u_id
from app.db.scheme.forumcommentlikes import ForumCommentLikes_Read, ForumCommentLikes_Count
from app.services.forumcommentlikes import ForumCommentLikesService

router=APIRouter(prefix="/forumcommentlike", tags=["ForumCommentLike"])



#게시글 댓글 좋아요 생성
@router.post("/create/{fc_id}")
async def router_forumcommentlikes_create(fc_id:int, 
                                          u_id:int=Depends(auth_get_u_id),
                                          db:AsyncSession=Depends(get_db)):
    return await ForumCommentLikesService.service_forumcommentlikes_create(db, fc_id, u_id)


#게시글 댓글 좋아요 취소
@router.delete("/del/{fc_id}")
async def router_forumcommentlikes_delete(fc_id: int,
                                          u_id: int=Depends(auth_get_u_id),
                                          db:AsyncSession=Depends(get_db)):
    return await ForumCommentLikesService.service_forumcommentlikes_delete(db, fc_id, u_id)


#게시글 좋아요 개수
@router.get("/count/{fc_id}", response_model=ForumCommentLikes_Count)
async def router_forumcommentlikes_count(fc_id: int,
                                         db:AsyncSession=Depends(get_db)):
    return await ForumCommentLikesService.service_forumcommentlikes_count(db, fc_id)
