from pydantic import BaseModel, Field, EmailStr, ConfigDict
from fastapi import status, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from sqlalchemy import or_, and_
from typing import Optional

from app.db.models.users import User
from app.db.crud.users import User_Crud
from app.db.models.care_group import Care_Group
from app.db.crud.parents import Parent_Crud
from app.db.models.parents import Parent

from app.db.models.alarms import Alarm
from app.db.scheme.alarms import Alarm_Base, Alarm_Create, Alarm_Read
from app.db.crud.alarms import Alarm_Crud


class Alarm_Service:

    # 알람 생성 + 공동 양육자 '초대됨' 목록 추가
    @staticmethod
    async def service_alarm_create(db: AsyncSession, send_id: int, receive_account: str, p_category: str):
        try:
            # 1. 계정으로 받는 사람(B) 찾기
            receiver = await User_Crud.crud_users_get_by_account(db, receive_account)
            if not receiver:
                raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="존재하지 않는 계정입니다")

            receive_id = receiver.u_id

            if receive_id == send_id:
                raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="자기 자신은 초대할 수 없습니다")

            # 2. 보내는 사람(A)의 그룹 확인
            sender = select(Parent).where(Parent.u_id == send_id)
            result_sender = await db.execute(sender)
            group_sender = result_sender.scalar_one_or_none()

            if not group_sender or group_sender.g_id is None:
                raise HTTPException(status_code=status.HTTP_444_NOT_RESPONSE, detail="보내는 사용자가 소속된 그룹이 없습니다")

            # 3. 받는 사람(B) 상태 검증
            receiver_parent = select(Parent).where(Parent.u_id == receive_id)
            result_receiver = await db.execute(receiver_parent)
            receiver_group = result_receiver.scalar_one_or_none()

            if receiver_group:
                # 상태가 '초대됨'이면서 나와 같은 그룹에서 보낸 초대 데이터가 이미 있다면 중복 초대 처리
                if receiver_group.p_state == "초대됨" and receiver_group.g_id == group_sender.g_id:
                    raise HTTPException(
                        status_code=status.HTTP_400_BAD_REQUEST,
                        detail="이미 공동 양육자로 초대 대기 중인 사용자입니다"
                    )
                # '초대됨' 대기 상태가 아니거나 확실하게 g_id를 가지고 활성화(active)된 유저라면 차단
                elif receiver_group.p_state == "active" and receiver_group.g_id is not None:
                    raise HTTPException(
                        status_code=status.HTTP_400_BAD_REQUEST,
                        detail="이미 다른 공동 양육 그룹에 속해 있는 사용자입니다"
                    )

            # 4. [Alarm] 테이블 데이터 생성 (알림 내용 보관)
            alarm_data = Alarm_Create(
                send_id=send_id,
                receive_id=receive_id,
                g_id=group_sender.g_id
            )
            db_data = await Alarm_Crud.crud_alarms_create(db, alarm=alarm_data)

            # 5. [Parent] 테이블 상태값 기록 및 가입 예비 데이터 준비
            if receiver_group:
                receiver_group.p_role = "공동 양육자"
                receiver_group.p_category = p_category
                receiver_group.p_state = "초대됨"
                receiver_group.g_id = group_sender.g_id  
                receiver_group.current_b_id = None  # ★ [수정] 초대 상태일 때는 아기 정보를 미리 연동하지 않음
            else:
                new_partner = Parent(
                    p_role="공동 양육자",
                    p_category=p_category,
                    p_state="초대됨",
                    g_id=group_sender.g_id,  
                    u_id=receive_id,
                    current_b_id=None  # ★ [수정] 초대 상태일 때는 아기 정보를 미리 연동하지 않음
                )
                db.add(new_partner)
            
            await db.flush()
            await db.commit()

            return db_data

        except HTTPException:
            await db.rollback()
            raise

        except Exception as e:
            await db.rollback()
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"알람 및 초대 생성 실패: {e}"
            )

    # 내 알람 목록
    @staticmethod
    async def service_alarm_list(db: AsyncSession, receive_id: int):
        try:
            alarms = await Alarm_Crud.crud_alarms_list(db, receive_id=receive_id)

            if not alarms:
                raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="알람 조회를 실패했습니다")

            result = []
            for alarm in alarms:
                sender = await User_Crud.crud_users_me(db, alarm.send_id)
                result.append({
                    "a_id": alarm.a_id,
                    "send_id": alarm.send_id,
                    "sender_name": sender.u_name if sender else "알 수 없음",
                    "receive_id": alarm.receive_id,
                    "g_id": alarm.g_id,
                    "a_created_at": alarm.a_created_at,
                })

            return result

        except HTTPException:
            raise
        except Exception as e:
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=f"알람 조회 실패: {e}")
        
    # 알람 삭제
    @staticmethod
    async def service_alarm_delete(db: AsyncSession, a_id: int):
        try:
            delete_alarm = await Alarm_Crud.crud_alarms_del(db, a_id=a_id)
            if not delete_alarm:
                raise HTTPException(status.HTTP_404_NOT_FOUND, detail="삭제 할 알람이 없음")
            
            await db.commit()
            return {"msg": "알람이 삭제되었습니다"}
        except HTTPException:
            raise
        except Exception as e:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"알람 삭제 실패: {e}"
            )
        
    # 알람 전체 삭제
    @staticmethod
    async def service_alarm_all_del(db: AsyncSession, receive_id: int):
        try:
            db_data = await Alarm_Crud.crud_alarms_all_del(db, receive_id)
            if not db_data:
                return {"msg": "삭제할 알람이 없습니다."}
            
            await db.commit()
            return {"msg": f"전체 알람이 {db_data}개 삭제되었습니다."}
        except HTTPException:
            raise
        except Exception as e:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"알람 전체 삭제 실패: {e}"
            )