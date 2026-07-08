from sqlalchemy.ext.asyncio import AsyncSession
from app.db.crud.milestones import Milestone_Crud

from app.db.models.babymilestones import BabyMilestone
from app.db.scheme.milestones import Milestone_Read, MilestoneStatus_Read
from app.db.scheme.babymilestones import BabyMilestone_Create, BabyMilestone_Update, BabyMilestone_Read
from fastapi import HTTPException, status

class MilestoneService:
    # 마일스톤&성공 여부 목록
    @staticmethod
    async def services_milestones_list(db : AsyncSession,
                                       b_id : int,
                                       months : int,
                                       category : str):
        try:
            result=await Milestone_Crud.crud_milestones_list(db, b_id, months, category)

            if not result:
                return []

            return result
        except Exception:
            raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, 
                                detail="마일스톤 목록 조회 실패")


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