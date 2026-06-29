from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from app.db.models.milestones import Milestone
from app.db.models.babymilestones import BabyMilestone
from datetime import datetime

class Milestone_Crud:
    @staticmethod
    async def crud_milestones_list(db: AsyncSession, months: int, category: str, b_id: int):
        stmt = select(Milestone).where(Milestone.m_months == months)
        if category:
            stmt = stmt.where(Milestone.m_category == category)
        
        result = await db.execute(stmt)
        milestones = result.scalars().all()
        
        # 아기별 달성 정보 조회
        if b_id:
            bm_stmt = select(BabyMilestone).where(BabyMilestone.b_id == b_id)
            bm_result = await db.execute(bm_stmt)
            achieved_map = {bm.m_id: bm.m_achieved for bm in bm_result.scalars().all()}
            
            # 응답 객체에 달성 여부 주입
            for m in milestones:
                m.is_achieved = achieved_map.get(m.m_id, False)
        
        return milestones

    @staticmethod
    async def crud_milestones_check(db: AsyncSession, b_id: int, milestone_id: int, is_achieved: bool):
        stmt = select(BabyMilestone).where(
            BabyMilestone.b_id == b_id, 
            BabyMilestone.m_id == milestone_id
        )
        result = await db.execute(stmt)
        bm = result.scalar_one_or_none()
        
        if bm:
            bm.m_achieved = is_achieved
            bm.m_achieved_date = datetime.now() if is_achieved else None
        else:
            new_bm = BabyMilestone(b_id=b_id, m_id=milestone_id, m_achieved=is_achieved, m_achieved_date=datetime.now() if is_achieved else None)
            db.add(new_bm)
        await db.flush()