from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession
from app.db.database import get_db
from app.services.milestones import MilestoneService
from app.db.scheme.milestones import Milestone_Read, MilestoneStatus_Read
from app.db.scheme.babymilestones import BabyMilestone_Read, BabyMilestone_Create, BabyMilestone_Update
from typing import Optional

router = APIRouter(prefix="/milestones", tags=["Milestone"])

@router.get("/list", response_model=list[MilestoneStatus_Read])
async def routers_milestones_list(b_id: int,
                                  category: str = "",
                                  target_age: Optional[int] = None,
                                  db: AsyncSession = Depends(get_db)):
        return await MilestoneService.services_milestones_list(db, b_id, category, target_age)


@router.post("/bm/create", response_model=BabyMilestone_Read)
async def routers_bm_create(data : BabyMilestone_Create,
                            db: AsyncSession = Depends(get_db)):
        return await MilestoneService.services_milestones_babymilestone_create(db, data)


@router.post("/bm/update", response_model=BabyMilestone_Read)
async def routers_bm_update(bm_id : int,
                            data : BabyMilestone_Update,
                            db: AsyncSession = Depends(get_db)):
        return await MilestoneService.services_milestones_babymilestone_update(db, data, bm_id)

@router.delete("/bm/del")
async def routers_bm_delete(bm_id : int,
                            db: AsyncSession = Depends(get_db)):
        return await MilestoneService.services_milestones_babymilestone_delete(db, bm_id)




