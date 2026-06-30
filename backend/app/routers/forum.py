#router_forums_create 게시물 생성
#router_forums_list 게시물 목록
# router_forums_context 게시물 상세
# router_forums_update 게시물 수정
# router_forums_delete 게시물 삭제


from typing import Optional
from urllib import response
from fastapi import APIRouter, Depends, Response, status, HTTPException, Request, Query
from sqlalchemy.ext.asyncio import AsyncSession
from pydantic import EmailStr

from app.db.database import get_db
from app.db.scheme.forums import Forum_Create, Forum_Update, Forum_Read
from app.services.forums import Forum_Service
from app.core.auth import auth_get_u_id, get_optional 


router=APIRouter(prefix="/forum", tags=["Forum"])

#게시글 생성
@router.post("/create", response_model=Forum_Read)
async def router_forums_create(forum_data: Forum_Create, u_id: int=Depends(auth_get_u_id), db:AsyncSession=Depends(get_db)):
    return await Forum_Service.service_forums_create(db, forum_data=forum_data, u_id=u_id)
     

#게시글 목록 조회
@router.get("/list", response_model=list[Forum_Read])
async def router_forums_list(tag: str | None=None,
                             baby_character: str | None=None,
                             sort: str | None=None,
                             u_id : int | None=Depends(get_optional),
                             db: AsyncSession=Depends(get_db)):
    return await Forum_Service.service_forums_list(db, tag=tag, baby_character=baby_character, sort=sort, u_id=u_id)
    

#게시글 상세 조회
@router.get("/context/{f_id}", response_model=Forum_Read)
async def router_forums_context(f_id: int,
                                u_id: int | None=Depends(get_optional),
                                db: AsyncSession=Depends(get_db)):
    return await Forum_Service.service_forums_context(db, f_id=f_id, u_id=u_id)


#게시글 정보 수정
@router.put("/edit")
async def router_forums_update(f_id: int,
                               forum_data: Forum_Update,
                               u_id: int=Depends(auth_get_u_id),
                               db: AsyncSession=Depends(get_db)):
    return await Forum_Service.service_forums_update(db, f_id=f_id, forum_data=forum_data, u_id=u_id)


#게시글 삭제
@router.delete("/del/{f_id}")
async def router_forums_delete(f_id: int,
                               u_id: int=Depends(auth_get_u_id),
                               db: AsyncSession=Depends(get_db)):
    await Forum_Service.service_forums_delete(db, f_id=f_id, u_id=u_id)
    return {"message": "게시글이 삭제되었습니다"}