#router_forums_create 게시물 생성
#router_forums_list 게시물 목록
# router_forums_context 게시물 상세
# router_forums_update 게시물 수정
# router_forums_delete 게시물 삭제


from typing import Optional
from urllib import response
from fastapi import APIRouter, Depends, File, Response, status, HTTPException, Request, Query, UploadFile, File
from sqlalchemy.ext.asyncio import AsyncSession
from pydantic import EmailStr
from enum import Enum
from app.db.database import get_db
from app.db.scheme.forums import Forum_Create, Forum_Update, Forum_Read
from app.services.forums import Forum_Service
from app.core.auth import auth_get_u_id, get_optional 
import os
import uuid

UPLOAD_DIR = "uploads/forum_images"
os.makedirs(UPLOAD_DIR, exist_ok=True)

router=APIRouter(prefix="/forums", tags=["Forum"])

#정렬 분류
class SortOption(str, Enum):
    latest= "latest"
    likes="likes"

#카테고리 분류
class TagOption(str, Enum):
    sleep = "sleep"
    food = "food"
    health = "health"
    play = "play"

#아기 기질 분류
class CharacterOption(str, Enum):
    curiosity = "curiosity"
    active = "active"
    shy = "shy"
    eater = "eater"
    sleepy = "sleepy"
    charm = "charm"
    my_baby = "my_baby"


#게시글 생성
@router.post("/create", response_model=Forum_Read)
async def router_forums_create(forum_data: Forum_Create, u_id: int=Depends(auth_get_u_id), db:AsyncSession=Depends(get_db)):
    return await Forum_Service.service_forums_create(db, forum_data=forum_data, u_id=u_id)
     

#게시글 목록 조회
@router.get("/list", response_model=list[Forum_Read])
async def router_forums_list(tag: TagOption | None = Query(None),
                             baby_character: CharacterOption | None = Query(None),
                             sort: SortOption=Query(SortOption.latest),
                             b_id: int | None = Query(None),
                             u_id : int | None=Depends(get_optional),
                             db: AsyncSession=Depends(get_db)):
    return await Forum_Service.service_forums_list(db, tag=tag.value if tag else None, 
                                                   baby_character=baby_character.value if baby_character else None, 
                                                   sort=sort.value, 
                                                   u_id=u_id,
                                                   b_id=b_id)
    

#게시글 상세 조회
@router.get("/context/{f_id}", response_model=Forum_Read)
async def router_forums_context(f_id: int,
                                u_id: int | None=Depends(get_optional),
                                db: AsyncSession=Depends(get_db)):
    return await Forum_Service.service_forums_context(db, f_id=f_id, u_id=u_id)


#게시글 정보 수정
@router.put("/edit/{f_id}")
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



@router.post("/upload_image")
async def router_forums_upload_image(file: UploadFile = File(...)):
    # 파일 이름에서 확장자(.jpg, .png 등) 분리
    ext = file.filename.split(".")[-1]
    # 고유한 랜덤 이름 생성
    new_filename = f"{uuid.uuid4()}.{ext}"
    # 저장할 경로 완성
    file_path = os.path.join(UPLOAD_DIR, new_filename)

    # 폴더에 사진 쓰기
    with open(file_path, "wb") as f:
        content = await file.read()
        f.write(content)

    # 리액트로 돌려줄 주소 생성
    image_url = f"/{file_path}"
    return {"image_url": image_url}