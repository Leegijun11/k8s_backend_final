#service_parents_create 양육자 등록
#service_parents_list 양육자 목록
#service_parents_delete 양육자 삭제




from pydantic import BaseModel, Field, EmailStr, ConfigDict
from fastapi import status, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from typing import Optional

from app.db.crud.parents import Parent_Crud
from app.db.scheme.parents import Parent_Create,Parent_Base,Parent_Update,Parent_Read
from app.db.models.parents import Parent
from app.db.models.users import User
from app.db.models.care_group import Care_Group


class Parent_Service:

    #양육자 등록
    @staticmethod
    async def service_parents_create(db:AsyncSession, parent:Parent_Create):
        try:
            await Parent_Crud.crud_parents_create(db, parent=parent)
            await db.commit()
            return{"msg":"공통 양육자를 초대했습니다"}
        
        except HTTPException:
            raise
        except Exception as e:
            await db.rollback()
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST,
                                detail=f"공동 양육자 초대에 실패했습니다:{e}")

    
    #양육자 목록
    @staticmethod
    async def service_parents_list(db:AsyncSession, u_id:int):
        try:
            #요청된 u_id를 기반으로 정보를 찾음
            me=select(Parent).where(Parent.u_id==u_id)
            result_me=await db.execute(me)
            me_data=result_me.scalar_one_or_none()

            if not me_data or me_data.g_id is None:
                raise HTTPException(status_code=status.HTTP_404_NOT_FOUND)

            #같은 그룹 멥버 리스트를 가져옴
            group_members = await Parent_Crud.crud_parents_list(db, g_id=me_data.g_id)
            if not group_members:
                raise HTTPException(status_code=status.HTTP_404_NOT_FOUND)
            
            #u_id,로 user테이블 일괄 조회
            member_u_id=[m.u_id for m in group_members]

            member_users=select(User.u_id, User.u_name).where(User.u_id.in_(member_u_id))
            result_users=await db.execute(member_users)
            #딕셔너리 변환
            user_name_map={row.u_id:row.u_name for row in result_users.all()}

            return [
                {
                    "p_id":member.p_id,
                    "u_name": user_name_map.get(member.u_id),
                    "p_role": member.p_role,
                    "p_category": member.p_category,
                    "p_state": member.p_state
                }
                for member in group_members
            ]
        
        except HTTPException:
            raise
        except Exception as e:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"공동 양육자 목록을 불러오는데 실패함: {e}"
            )
        

    #양육자 삭제
    @staticmethod
    async def service_parents_delete(db:AsyncSession, p_id:int):
        try:
            query=select(Parent).where(Parent.p_id==p_id)
            result=await db.execute(query)
            db_data=result.scalar_one_or_none()

            if not db_data:
                raise HTTPException(status.HTTP_404_NOT_FOUND)
            
            await Parent_Crud.crud_parents_del(db, p_id=db_data.p_id)
            await db.commit()

            return{"detail":"공동 양육자 지정이 취소되었습니다"}
        
        except HTTPException:
            raise
        except Exception as e:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"공동 양육자 지정이 취소가 실패되었습니다: {e}"
            )