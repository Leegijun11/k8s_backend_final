from sqlalchemy.ext.asyncio import AsyncSession
from app.db.crud.milestones import Milestone_Crud

from app.db.models.babymilestones import BabyMilestone
from app.db.scheme.milestones import Milestone_Read, MilestoneStatus_Read
from app.db.scheme.babymilestones import BabyMilestone_Create, BabyMilestone_Update, BabyMilestone_Read
from app.db.crud.babies import Baby_Crud
from fastapi import HTTPException, status
from datetime import datetime, date
from typing import Optional

class MilestoneService:
    # 마일스톤&성공 여부 목록
    @staticmethod
    async def services_milestones_list(db : AsyncSession,
                                       b_id : int,
                                       category : str,
                                       target_age : Optional[int] = None):
        try:
            if target_age is None:
                baby_date = await Baby_Crud.crud_babies_detail(db, b_id)
                b_date = baby_date.b_birth

                if isinstance(b_date, datetime):
                    b_date = b_date.date()
                elif isinstance(b_date, str):
                    b_date = datetime.strptime(b_date, "%Y-%m-%d %H:%M:%S").date()

                days = (date.today() - b_date).days
                age = int(days / 30.43)
                age = max(0, age)
            else:
                age = target_age

            # CRUD는 건드리지 않았습니다. 기존 인터페이스 그대로 호출합니다.
            result = await Milestone_Crud.crud_milestones_list(db, b_id, age, category)

            if not result:
                return []

            return result
        except Exception as e:
            raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, 
                                detail=f"마일스톤 목록 조회 실패 : {e}")

    @staticmethod
    async def services_milestones_achieved_count(db: AsyncSession, b_id: int) -> int:
        try:
            return await Milestone_Crud.crud_milestones_achieved_count(db, b_id)
        except Exception as e:
            raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                                detail=f"달성 마일스톤 수 조회 실패: {e}")

    # 베이비 마일스톤 생성
    @staticmethod
    async def services_milestones_babymilestone_create(db : AsyncSession,
                                                       data : BabyMilestone_Create) -> BabyMilestone_Read:
        try:
            result = await Milestone_Crud.crud_milestones_babymilestone_create(db, data)
        
            if not result:
                raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST,
                                    detail="아기 마일스톤 생성에 실패했습니다.")
            
            await db.commit()
            return result

        except Exception:
            await db.rollback()
            raise 
        

    # 베이비 마일스톤 수정
    @staticmethod
    async def services_milestones_babymilestone_update(db : AsyncSession,
                                                       data : BabyMilestone_Update,
                                                       bm_id : int) -> BabyMilestone_Read:
        try:
            result = await Milestone_Crud.crud_milestones_babymilestone_update(db, data, bm_id)
        
            if not result:
                raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST,
                                    detail="아기 마일스톤 수정에 실패했습니다.")
            
            await db.commit()
            return result

        except Exception:
            await db.rollback()
            raise 


    # 베이비 마일스톤 삭제
    @staticmethod
    async def services_milestones_babymilestone_delete(db : AsyncSession,
                                                       bm_id : int) -> dict:
        try:
            result = await Milestone_Crud.crud_milestones_babymilestone_del(db, bm_id)
        
            if not result:
                raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST,
                                    detail="아기 마일스톤 삭제에 실패했습니다.")
            
            await db.commit()
            return {"msg" : "아기 마일스톤을 삭제했습니다."}

        except Exception:
            await db.rollback()
            raise 