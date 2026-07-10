from fastapi import APIRouter, Depends, status
from sqlalchemy.ext.asyncio import AsyncSession
from app.db.database import get_db 
from app.core.auth import auth_get_u_id
from app.db.scheme.forumcomments import ForumComment_Create, ForumComment_Update, ForumComment_Read
from app.services.forumcomments import ForumCommentService

router = APIRouter(prefix="/forumcomment", tags=["ForumComment"])

# 1. 댓글 등록
@router.post("/create/{f_id}",  response_model=ForumComment_Read)
async def router_forumcomments_create(f_id: int,
                                      comment:ForumComment_Create,
                                      u_id: int=Depends(auth_get_u_id),
                                      db:AsyncSession=Depends(get_db)):
    
    return await ForumCommentService.service_forumcomments_create(db, f_id, u_id, comment)

#댓글 조회
@router.get("/list/{f_id}", response_model=list[ForumComment_Read])
async def router_forumcomments_list(f_id: int,
                                    u_id: int = Depends(auth_get_u_id),
                                    db: AsyncSession=Depends(get_db)):
    return await ForumCommentService.service_forumcomments_list(db, f_id, u_id)


#댓글 수정
@router.put('/update/{fc_id}', response_model=ForumComment_Read)
async def router_forumcomments_update(fc_id:int,
                                      comment: ForumComment_Update,
                                      u_id:int=Depends(auth_get_u_id),
                                      db:AsyncSession=Depends(get_db)):
    return await ForumCommentService.service_forumcomments_update(db, fc_id, u_id, comment)


#댓글 삭제
@router.delete("/del/{fc_id}")
async def router_forumcomments_delete(fc_id:int,
                                      u_id:int=Depends(auth_get_u_id),
                                      db:AsyncSession=Depends(get_db)):
    await ForumCommentService.service_forumcomments_delete(db, fc_id, u_id)

    return {"message": "댓글이 정상적으로 삭제되었습니다."}

