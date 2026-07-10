#router_users_singup: 회원가입
#router_users_login: 로그인
#router_users_logout: 로그아웃
#router_users_me: 현재 유저 정보 
#router_users_find_account: 아이디 찾기
#router_users_search: 아이디로 유저 검색
#router_users_update: 유저 수정
#router_users_delete: 유저 삭제
#router_users_get_u_id: 다른 유저 정보

from fastapi import APIRouter, Depends, Response, status, HTTPException, Request
from sqlalchemy.ext.asyncio import AsyncSession
from pydantic import EmailStr
from app.db.scheme.users import User_Create, User_Update, User_Login, User_Public, User_Read
from app.services.users import User_Service
from app.core.auth import set_auth_cookies, auth_get_u_id
from app.db.database import get_db
import os
import uuid
from fastapi import UploadFile, File

UPLOAD_DIR = "uploads/user_images"
os.makedirs(UPLOAD_DIR, exist_ok=True)
router=APIRouter(prefix="/users",tags=["Users"])

#회원가입
@router.post('/signup',response_model=User_Read)
async def router_users_singup(user:User_Create, db:AsyncSession=Depends(get_db)):
    return await User_Service.services_user_create(db, user)

#로그인
@router.post('/login')
async def router_users_login(user:User_Login, response:Response, db:AsyncSession=Depends(get_db)):
    result=await User_Service.services_user_login(db, user)
    db_user, access_token, refresh_token=result
    set_auth_cookies(response, access_token, refresh_token)
    return db_user


#로그아웃
@router.post('/logout')
async def router_users_logout(response:Response,u_id: int=Depends(auth_get_u_id), db:AsyncSession=Depends(get_db)):
    await User_Service.service_users_logout(db, u_id)
    response.delete_cookie("access_token", path="/")
    response.delete_cookie("refresh_token", path="/")
    return {"message": "로그아웃 성공"}

#아이디 중복확인
@router.get('/check_account')
async def router_users_check_account(u_account: str, db: AsyncSession = Depends(get_db)):
    return await User_Service.service_users_check_account(db, u_account)

#현재 유저 정보
@router.get('/me', response_model=User_Read)
async def router_users_me(u_id:int=Depends(auth_get_u_id), db:AsyncSession=Depends(get_db)):
    user_data=await User_Service.service_users_me(db, u_id)
    return user_data



#아이디 찾기
@router.get('/find_account')
async def router_users_find_account(u_name:str, u_email:EmailStr,u_phone:str, db:AsyncSession=Depends(get_db)):
    return await User_Service.service_users_find_account(db, u_name, u_email,u_phone)


# 비밀번호 찾기
@router.post('/find_pw')
async def router_users_find_pw(u_account: str,
                               u_name: str,
                               u_email: EmailStr,
                               u_phone: str, 
                               db: AsyncSession = Depends(get_db)):
    
    return await User_Service.service_users_find_pw(db,
                                                    u_account,
                                                    u_name,
                                                    u_email,
                                                    u_phone)


#유저 정보 수정
@router.put('/edit', response_model=dict)
async def router_users_update(user_update:User_Update, u_id:int=Depends(auth_get_u_id), db: AsyncSession = Depends(get_db)):
    return await User_Service.service_users_update(db, u_id, user_update)


#유저 삭제
@router.delete('/del', status_code=status.HTTP_204_NO_CONTENT)
async def router_users_delete(response:Response, u_id:int=Depends(auth_get_u_id), db:AsyncSession=Depends(get_db)):
    return await User_Service.service_users_delete(db, u_id)
    #쿠키 삭제(보류)


#다른 유저 정보
@router.get('/{u_id}',response_model=User_Public)
async def router_users_get_u_id(u_id:int, db:AsyncSession=Depends(get_db)):
    other_user_data=await User_Service.service_users_get_u_id(db, u_id)
    return other_user_data

@router.post("/upload_image")
async def router_users_upload_image(file: UploadFile = File(...)):
    ext = file.filename.split(".")[-1]
    new_filename = f"{uuid.uuid4()}.{ext}"
    file_path = os.path.join(UPLOAD_DIR, new_filename)

    with open(file_path, "wb") as f:
        content = await file.read()
        f.write(content)

    image_url = f"/{file_path}"
    return {"image_url": image_url}