from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession
from app.db.database import get_db
from app.services.milestones import MilestoneService
from app.db.scheme.milestones import Milestone_Read

router = APIRouter(prefix="/milestones", tags=["Milestone"])

@router.get("/list", response_model=list[Milestone_Read])
async def routers_milestone_list(
    months: int,
    category: str = "",
    b_id: int = None, # 달성 여부 확인을 위해 추가 가능
    db: AsyncSession = Depends(get_db)
):
    return await MilestoneService.service_milestones_list(db, months, category, b_id)

@router.post("/check")
async def routers_milestone_check(
    b_id: int,
    milestone_id: int,
    is_achieved: bool,
    db: AsyncSession = Depends(get_db)
):
    return await MilestoneService.service_milestones_check(db, b_id, milestone_id, is_achieved)