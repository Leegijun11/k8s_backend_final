from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func, desc
from sqlalchemy.orm import joinedload
from app.db.models.milestones import Milestone
from app.db.models.babymilestones import BabyMilestone

from app.db.scheme.milestones import Milestone_Read, MilestoneStatus_Read
from app.db.scheme.babymilestones import BabyMilestone_Create, BabyMilestone_Update

from datetime import date

class Milestone_Crud:
    # 마일스톤 리스트
    @staticmethod
    async def crud_milestones_list(db : AsyncSession,
                                   b_id : int, 
                                   months : int, 
                                   category : str) -> list[MilestoneStatus_Read] | None:
        margin = 2 if months < 24 else 1
        min_months = max(0, months - margin)
        max_months = months + margin

        sub_query = (
            select(
                BabyMilestone.bm_id,
                BabyMilestone.m_id,
                BabyMilestone.m_achieved,
                BabyMilestone.m_achieved_date,
                BabyMilestone.d_id,
                func.row_number().over(
                    partition_by=BabyMilestone.m_id,
                    order_by=[BabyMilestone.m_achieved.desc(), BabyMilestone.bm_id.desc()]
                ).label("row_num")
            )
            .where(BabyMilestone.b_id == b_id)
            .subquery()
        )

        query = (
            select(Milestone, sub_query)
            .outerjoin(sub_query, (Milestone.m_id == sub_query.c.m_id) & (sub_query.c.row_num == 1))
            .where(Milestone.m_months.between(min_months, max_months))
        )

        if category and category.strip():
            query = query.where(Milestone.m_category == category)
            
        results = await db.execute(query)
        db_rows = results.all()
        
        return [MilestoneStatus_Read(m_id=m.m_id, 
                                     m_months=m.m_months, 
                                     m_category=m.m_category,
                                     app_milestone=m.app_milestone,
                                     
                                     bm_id=row[0] if row[0] else None,
                                     is_achieved=bool(row[2]) if row[0] else False,
                                     m_achieved_date=row[3] if row[0] else None,
                                     d_id=row[4] if row[0] else None)
                                     for m, *row in db_rows]


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
                                  .where(BabyMilestone.b_id==b_id)
                                  .order_by(desc(BabyMilestone.m_achieved_date)))
        return result.scalars().first()

    
    # 베이비 마일스톤 기간내 목록
    @staticmethod
    async def crud_milestones_bm_date_list(db : AsyncSession,
                                         b_id : int,
                                         start_date : date,
                                         end_date : date):
        result = await db.execute(select(BabyMilestone)
                                  .where(BabyMilestone.b_id==b_id)
                                  .where(BabyMilestone.m_achieved_date.between(start_date, end_date))
                                  .options(joinedload(BabyMilestone.milestone)) )
        return result.scalars().all()


    # 베이비 마일스톤 m_id가 동일한 실패 목록
    @staticmethod
    async def crud_milestones_bm_false_list(db : AsyncSession,
                                         b_id : int,
                                         m_id : int):
        result = await db.execute(select(BabyMilestone)
                                  .where(BabyMilestone.b_id==b_id)
                                  .where(BabyMilestone.m_id==m_id)
                                  .where(BabyMilestone.m_achieved==False))
        return result.scalars().all()

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
                                                   bm_id : int,
                                                   data : BabyMilestone_Update):
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