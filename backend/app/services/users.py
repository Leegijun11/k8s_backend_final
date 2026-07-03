#service_users_singup: 회원가입
#service_users_login: 로그인
#service_users_logout: 로그아웃
#service_users_me: 현재 유저 정보 
#service_users_get_u_id: 다른 유저 정보
#service_users_find_account: 아이디 찾기
#service_users_update: 유저 수정
#service_users_delete: 유저 삭제

from pydantic import BaseModel, Field, EmailStr, ConfigDict
from fastapi import status, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from typing import Optional
from app.db.scheme.users import User_Create, User_Update, User_Login, User_Base
from app.db.crud.users import User_Crud
from app.core.jwt_handle import get_password_hash, verify_password
from app.core.auth import set_auth_cookies, auth_get_u_id
from app.core.jwt_handle import create_access_token, create_refresh_token
from app.core.settings import Settings
from app.core.mail import generate_verification_code, send_verification_email_async


class User_Service:

    # 회원가입
    @staticmethod
    async def services_user_create(db: AsyncSession, user: User_Create):
        try:
            #아이디 중복 확인
            existing_account = await User_Crud.crud_users_get_by_account(db, user.u_account)
            if existing_account:
               raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="이미 사용중인 아이디입니다.")
            
            #이메일/전화번호 중복 확인
            existing_email = await User_Crud.crud_users_get_by_email(db, user.u_email)
            if existing_email:
                raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="이미 사용중인 이메일입니다.")
                
            #전화번호 중복 확인
            existing_phone = await User_Crud.crud_users_get_by_phone(db, user.u_phone)
            if existing_phone:
                raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="이미 사용중인 전화번호입니다.")
            
            hashed_pw=get_password_hash(user.u_pw)

            new_user=await User_Crud.crud_users_signup(db, user, hashed_pw)
            
            await db.commit()
            await db.refresh(new_user)
            
            return {
                "u_id":new_user.u_id,
                "u_account": new_user.u_account,
                "u_pw": new_user.u_pw,
                "u_name": new_user.u_name,
                "u_nickname": new_user.u_nickname,
                "u_email": new_user.u_email,
                "u_phone": new_user.u_phone,
                "u_created_at": new_user.u_created_at,
                "u_address": new_user.u_address,
                "u_image": new_user.u_image
            }
        except HTTPException:
            raise

        except Exception as e:
            await db.rollback()
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST, 
                detail=f"회원가입 실패: {e}"  
            )
        
    #아이디 중복검사
    @staticmethod
    async def service_users_check_account(db: AsyncSession, u_account: str):
        existing = await User_Crud.crud_users_get_by_account(db, u_account)
        return {"available": existing is None}
        
        

    #로그인
    @staticmethod
    async def services_user_login(db: AsyncSession, login_data: User_Login):
        try:
            user = await User_Crud.crud_users_get_by_account(db, login_data.u_account)
            
            #verify_password 결과가 false면 (유저가 없거나) 실패
            if not user or not verify_password(login_data.u_pw, user.u_pw):
                raise HTTPException(
                    status_code=status.HTTP_401_UNAUTHORIZED, 
                    detail="로그인 실패" 
                )

            token_data={"sub": str(user.u_id), "u_account": user.u_account,"u_name": user.u_name}
            access_token=create_access_token(u_id=user.u_id, **token_data)
            refresh_token = create_refresh_token(u_id=user.u_id)

            await User_Crud.crud_users_update_token(db, user.u_id, refresh_token)

            response_data={"u_id":user.u_id,"u_account":user.u_account,"u_name":user.u_name}

            await db.commit()
            return response_data, access_token, refresh_token
        
        
        except HTTPException:
            raise

        except Exception as e:
            await db.rollback()
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, 
                detail=f"로그인 실패 :{e}")
        

    #로그아웃
    @staticmethod
    async def service_users_logout(db:AsyncSession, u_id:int):
        try:
            await User_Crud.crud_users_update_token(db, u_id, None)

            await db.commit()
            return{"msg":"로그아웃"}

        except Exception as e:
            await db.rollback()
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=f"로그아웃 실패: {e}"
            )
        

    #현재 유저 정보
    @staticmethod
    async def service_users_me(db:AsyncSession, u_id:int):
        try:
            user=await User_Crud.crud_users_me(db, u_id)

            if not user:
                raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,detail="유저 정보 확인 실패")
            
            return user
        
        except HTTPException:
            raise

        except Exception as e:
            raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, 
                                detail=f"유저 정보 조회중 에러 발생: {e}")
        


        except Exception as e:
            raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, 
                                detail=f" 다른 유저 정보중 에러 발생: {e}")
        
        
    # 아이디(u_account)로 유저 검색
    @staticmethod
    async def service_users_search(db: AsyncSession, u_account: str):
        try:
            user = await User_Crud.crud_users_get_by_account(db, u_account)

            if not user:
                raise HTTPException(
                    status_code=status.HTTP_404_NOT_FOUND,
                    detail="사용자를 찾을 수 없습니다."
            )

            return {
                "u_id": user.u_id,
                "u_account": user.u_account,
                "u_name": user.u_name
        }

        except HTTPException:
            raise

        except Exception as e:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=f"사용자 검색 실패 : {e}"
            )
        

    #아이디 찾기
    @staticmethod
    async def service_users_find_account(db: AsyncSession, u_name:str, u_email:EmailStr, u_phone:str):
        try:
            user=await User_Crud.crud_users_u_account_by_udata(db, u_name, u_email,u_phone)


            if not user or not user.u_account:
                raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="정보와 일치하는 회원을 찾을수 없음")
            
            raw_id=user.u_account

            if len(raw_id) <= 3:
                hidden_id=raw_id[0] + "*" * (len(raw_id) - 1)
            else:
                hidden_id=raw_id[:3]+"*" *(len(raw_id) - 3)

            return{"u_account":hidden_id}
            
        except HTTPException:
            raise

        except Exception as e:
            raise HTTPException(
                status_code=status .HTTP_500_INTERNAL_SERVER_ERROR,
                detail=f"아이디 찾기 중 서버 오류: {e}"
            )
        

    # 비밀번호 찾기
    @staticmethod
    async def service_users_find_pw(db: AsyncSession, 
                                    u_account: str, 
                                    u_name: str, 
                                    u_email: EmailStr, 
                                    u_phone: str):
        try:
            user = await User_Crud.crud_users_u_pw_by_udata(db, 
                                                            u_account, 
                                                            u_name, 
                                                            u_email, 
                                                            u_phone)
            
            if not user:
                raise HTTPException(
                    status_code=status.HTTP_404_NOT_FOUND, 
                    detail="입력하신 정보와 일치하는 회원을 찾을 수 없습니다."
                )

            temp_pw = generate_verification_code(length=8)
            hashed_pw = get_password_hash(temp_pw)

            update_model = User_Update(u_pw=hashed_pw)
            updated_user = await User_Crud.crud_users_update(db, user.u_id, update_model)
            if not updated_user:
                raise HTTPException(
                    status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                    detail="임시 비밀번호 업데이트에 실패했습니다."
                )

            try:
                await send_verification_email_async(
                    email_to=user.u_email,
                    u_name=user.u_name,
                    auth_code=temp_pw
                )
            except RuntimeError as mail_error:
                await db.rollback()
                raise HTTPException(
                    status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                    detail=f"메일 발송에 실패하여 임시 비밀번호 발급이 취소되었습니다: {mail_error}"
                )

            await db.commit()

            return {
                "status": "success",
                "message": "회원님의 이메일로 임시 비밀번호가 안전하게 발급 및 전송되었습니다."
            }

        except HTTPException:
            raise
        except Exception as e:
            await db.rollback()
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=f"비밀번호 찾기 처리 중 서버 오류가 발생했습니다: {e}"
            )


    #유저 정보 수정
    @staticmethod
    async def service_users_update(db:AsyncSession, u_id:int, update_user:User_Update):
        try:
            updated_data=update_user.model_dump(exclude_unset=True)

            if updated_data.get("u_pw"):
                updated_data['u_pw']=get_password_hash(updated_data["u_pw"])

            updated_model=User_Update(**updated_data)

            updated_user=await User_Crud.crud_users_update(db, u_id, updated_model)

            if not updated_user:
                raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="정보 수정에 실패")

            await db.commit()
            await db.refresh(updated_user)
            return{"msg":"정보를 수정함"}

        except HTTPException:
            raise
        except Exception as e:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=f"정보 수정에 실패했습니다{e}"
            )
    
    #유저 삭제
    @staticmethod
    async def service_users_delete(db:AsyncSession, u_id:int):
        try:
            delete_user=await User_Crud.crud_users_del(db, u_id)

            if not delete_user:
                raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="삭제할 유저 없음")
            
            await db.commit()
            return{"msg":"삭제 성공"}
        except HTTPException:
            raise
        except Exception as e:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=f"정보 삭제에 실패했습니다{e}"
            )
        
    #다른 유저 정보
    @staticmethod
    async def service_users_get_u_id(db: AsyncSession, other_u_id:int):
        try:
            user=await User_Crud.crud_users_me(db, other_u_id)
            if not user:
                raise HTTPException(
                    status_code=status.HTTP_404_NOT_FOUND, detail="다른 유저 정보 없음"
                )
            return{
                    "u_account":user.u_account,
                    "u_nickname":user.u_nickname,
                    "u_created_at":user.u_created_at
                }
        except HTTPException:
            raise
            


            
