from fastapi import APIRouter, Depends, status
from sqlalchemy.ext.asyncio import AsyncSession
from app.db.database import get_db 
from app.core.auth import get_current_user 
from app.db.scheme.forumcomments import ForumComment_Create, ForumComment_Update, ForumComment_Read
from app.services.forumcomments import ForumCommentService

router = APIRouter(prefix="/forumcomment", tags=["ForumComment"])

# 1. 댓글 등록
@router.post("/create/{f_id}",  response_model=ForumComment_Read)
async def router_forumcomments_create()