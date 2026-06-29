from sqlalchemy.ext.asyncio import AsyncSession
from app.db.crud.milestones import Milestone_Crud
from fastapi import HTTPException

class MilestoneService:
    @staticmethod
    async def service_milestones_list(db: AsyncSession, months: int, category: str, b_id: int):
        try:
            return await Milestone_Crud.crud_milestones_list(db, months, category, b_id)
        except Exception:
            raise HTTPException(status_code=500, detail="마일스톤 목록 조회 실패")

    @staticmethod
    async def service_milestones_check(db: AsyncSession, b_id: int, milestone_id: int, is_achieved: bool):
        try:
            await Milestone_Crud.crud_milestones_check(db, b_id, milestone_id, is_achieved)
            await db.commit()
            return {"message": "Success"}
        except Exception:
            await db.rollback()
            raise HTTPException(status_code=500, detail="마일스톤 상태 변경 실패")