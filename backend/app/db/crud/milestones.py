from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from app.db.models.milestones import Milestone
from app.db.models.babymilestones import BabyMilestone

from app.db.scheme.milestones import Milestone_Read, MilestoneStatus_Read
from app.db.scheme.babymilestones import BabyMilestone_Create, BabyMilestone_Update

class Milestone_Crud:
    # 마일스톤 리스트
    @staticmethod
    async def crud_milestones_list(db : AsyncSession,
                                   b_id : int, 
                                   months : int, 
                                   category : str) -> list[MilestoneStatus_Read] | None:
        query = (select(Milestone, BabyMilestone)
                .outerjoin(BabyMilestone, (Milestone.m_id == BabyMilestone.m_id) & (BabyMilestone.b_id == b_id))
                .where(Milestone.m_months == months)
                .where(Milestone.m_category == category))
            
        results = await db.execute(query)
        db_rows = results.all()
        
        return [MilestoneStatus_Read(m_id=m.m_id, 
                                     m_months=m.m_months, 
                                     m_category=m.m_category,
                                     app_milestone=m.app_milestone,
                                     
                                     bm_id=bm.bm_id if bm else None,
                                     is_achieved=True if bm else False,
                                     m_achieved_date=bm.m_achieved_date if bm else None,
                                     d_id=bm.d_id if bm else None)
                                     for m, bm in db_rows]


    # 마일스톤 조회
    @staticmethod
    async def crud_milestones_find(db : AsyncSession,
                                   app_milestone : str,
                                   age : int):
        result = await db.execute(select(Milestone.m_id)
                                  .where(Milestone.app_milestone==app_milestone)
                                  .where(Milestone.m_months<=age))
        return result.scalars().one_or_none()
    

    # 베이비 마일스톤 조회
    @staticmethod
    async def crud_milestones_babymilestone_find(db : AsyncSession,
                                                 m_id : int,
                                                 b_id : int):
        result = await db.execute(select(BabyMilestone)
                                  .where(BabyMilestone.m_id==m_id)
                                  .where(BabyMilestone.b_id==b_id))
        return result.scalars().one_or_none()


    # 베이비 마일스톤 생성
    @staticmethod
    async def crud_milestones_babymilestone_create(db : AsyncSession, 
                                                   data : BabyMilestone_Create):
        db_data=BabyMilestone(**data.model_dump())
        db.add(db_data)
        await db.flush()
        return db_data
    

    # 베이비 마일스톤 수정
    @staticmethod
    async def crud_milestones_babymilestone_update(db : AsyncSession,
                                                   data : BabyMilestone_Update,
                                                   bm_id : int):
        db_data=await db.get(BabyMilestone, bm_id)
        
        if db_data:           
            update_data= data.model_dump(exclude_unset=True)

            for key, value in update_data.items():
                setattr(db_data, key, value)

            await db.flush()
            return db_data
            
        return None


    # 베이비 마일스톤 삭제
    @staticmethod
    async def crud_milestones_babymilestone_del(db:AsyncSession , 
                                                bm_id:int):
        db_data = await db.get(BabyMilestone, bm_id)
        if db_data:
            await db.delete(db_data)
            await db.flush()
            return db_data
        return None