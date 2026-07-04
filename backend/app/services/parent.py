from app.db.models.parents import Parent
from pydantic import BaseModel, Field, EmailStr, ConfigDict
from fastapi import status, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from typing import Optional

from app.db.crud.parents import Parent_Crud
from app.db.scheme.parents import Parent_Create, Parent_Base, Parent_Update, Parent_Read
from app.db.models.users import User
from app.db.models.care_group import Care_Group
from app.db.models.babies import Baby
from app.db.crud.babies import Baby_Crud

class Parent_Service:

    # 양육자 등록 (알람 수락 시 호출됨)
    @staticmethod
    async def service_parents_create(db: AsyncSession, parent: Parent_Create):
        try:
            # 1. 이미 그룹에 속해있는지 재확인
            existing = select(Parent).where(Parent.u_id == parent.u_id)
            result_existing = await db.execute(existing)
            existing_parent = result_existing.scalar_one_or_none()

            # g_id가 있으면서 '정식 활성화(active)' 상태인 유저만 진짜로 차단합니다.
            if existing_parent and existing_parent.g_id is not None and existing_parent.p_state == "active":
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail="이미 다른 공동 양육 그룹에 속해 있습니다"
                )

            # [수정] 수락하는 시점에 초대한 그룹의 첫 번째 아기 정보를 가져와 할당합니다.
            first_baby = await Baby_Crud.crud_babies_get_first_by_g_id(db, parent.g_id)
            parent_data = parent.model_dump()

            # 이미 '초대됨' 상태로 row가 생성되어 있다면 새로 add하지 않고 업데이트 처리
            if existing_parent:
                existing_parent.p_role = parent.p_role or "공동 양육자"
                existing_parent.p_category = parent.p_category
                existing_parent.p_state = "active"  # 수락했으므로 정식 활성화 상태로 전환!
                existing_parent.g_id = parent.g_id
                if first_baby:
                    existing_parent.current_b_id = first_baby.b_id  # 수락 시점에 아기 ID 주입
            else:
                # 데이터가 아예 없는 예외적인 케이스를 위한 정식 생성
                parent_data["p_state"] = "active"
                if first_baby:
                    parent_data["current_b_id"] = first_baby.b_id
                db_data = Parent(**parent_data)
                db.add(db_data)
                
            await db.flush()
            await db.commit()

            return {"msg": "공동 양육자 초대를 수락하였습니다"}

        except HTTPException:
            await db.rollback()
            raise

        except Exception as e:
            await db.rollback()
            print("ERROR >>>", repr(e))
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"공동 양육자 초대에 실패했습니다: {e}"
            )

    # 양육자 목록
    @staticmethod
    async def service_parents_list(db: AsyncSession, u_id: int):
        try:
            me = select(Parent).where(Parent.u_id == u_id)
            result_me = await db.execute(me)
            me_data = result_me.scalars().first()

            # 수락 대기 상태('초대됨')인 유저는 본인의 그룹 리스트를 조회할 수 없도록 방어
            if not me_data or me_data.g_id is None or me_data.p_state != "active":
                raise HTTPException(status_code=status.HTTP_404_NOT_FOUND)

            group_members = await Parent_Crud.crud_parents_list(db, g_id=me_data.g_id)
            if not group_members:
                raise HTTPException(status_code=status.HTTP_404_NOT_FOUND)
            
            filtered_members = [
                m for m in group_members 
                if m.p_state != "초대됨" or m.u_id != u_id
            ]

            member_u_id = [m.u_id for m in filtered_members]

            if not member_u_id:
                return []

            member_users = select(User.u_id, User.u_name, User.u_image).where(User.u_id.in_(member_u_id))
            result_users = await db.execute(member_users)
            
            user_map = {row.u_id: {"u_name": row.u_name, "u_image": row.u_image} for row in result_users.all()}

            return [
                {
                    "p_id": member.p_id,
                    "u_name": user_map.get(member.u_id, {}).get("u_name"),
                    "u_image": user_map.get(member.u_id, {}).get("u_image"),
                    "p_role": member.p_role,
                    "p_category": member.p_category,
                    "p_state": member.p_state
                }
                for member in filtered_members
            ]
        
        except HTTPException:
            raise
        except Exception as e:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"공동 양육자 목록을 불러오는데 실패함: {e}"
            )

    # 양육자 찾기
    @staticmethod
    async def services_parent_find(db: AsyncSession, u_id: int, g_id: int):
        try:
            Parent_data = await Parent_Crud.crud_parents_find(db, u_id, g_id)
            if not Parent_data:
                raise HTTPException(
                    status_code=status.HTTP_404_NOT_FOUND,
                    detail="양육자를 찾을 수 없습니다."
                )
            return Parent_data
        except HTTPException:
            raise
        except Exception as e:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=f"양육자 조회 실패: {e}"
            )

    # 양육자 업데이트
    @staticmethod
    async def services_parent_update(db: AsyncSession, p_id: int, parent: Parent_Update):
        try:
            update_data = parent.model_dump(exclude_unset=True)
            update_user = await Parent_Crud.crud_parents_update(db, p_id, parent)
            
            if not update_user:
                raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="수정할 수 없습니다")
                        
            await db.commit()
            await db.refresh(update_user)
            return update_user
        except HTTPException:
            await db.rollback()
            raise
        except Exception as e:
            await db.rollback()
            raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=f"양육자 정보 수정 실패 :{e}")

    # 양육자 삭제
    @staticmethod
    async def service_parents_delete(db: AsyncSession, p_id: int):
        try:
            query = select(Parent).where(Parent.p_id == p_id)
            result = await db.execute(query)
            db_data = result.scalar_one_or_none()

            if not db_data:
                raise HTTPException(status.HTTP_404_NOT_FOUND)
            
            await Parent_Crud.crud_parents_del(db, p_id=db_data.p_id)
            await db.commit()
            return {"detail": "공동 양육자 지정이 취소되었습니다"}
        except HTTPException:
            raise
        except Exception as e:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"공동 양육자 지정이 취소가 실패되었습니다: {e}"
            )
        
    # 현재 아이 설정
    @staticmethod
    async def service_parents_set_current_baby(db: AsyncSession, u_id: int, b_id: int):
        try:
            updated = await Parent_Crud.crud_parents_set_current_baby(db, u_id, b_id)
            if not updated:
                raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="유저 정보를 찾을 수 없습니다")
            await db.commit()
            return {"msg": "현재 아이가 변경되었습니다.", "current_b_id": b_id}
        except HTTPException:
            raise
        except Exception as e:
            await db.rollback()
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=f"현재 아이 설정 실패: {e}")

    # 현재 아이 조회 (★ 핵심 수정 핵심 포인트!)
    @staticmethod
    async def service_parents_get_current_baby(db: AsyncSession, u_id: int):
        try:
            parent = await Parent_Crud.crud_parents_get_current_baby(db, u_id)

            # ★ [수정] 수락 대기 상태('초대됨')이거나 선택된 아이 ID가 없으면 아이 정보를 노출하지 않습니다.
            if not parent or not parent.current_b_id or parent.p_state != "active":
                raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="선택된 아이가 없습니다")

            baby = await db.get(Baby, parent.current_b_id)

            if not baby:
                raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="아이 정보를 찾을 수 없습니다")

            return baby

        except HTTPException:
            raise
        except Exception as e:
            raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=f"현재 아이 조회 실패: {e}")