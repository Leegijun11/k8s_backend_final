from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from typing import Optional
from app.db.models.tips import Tip


class Tip_Crud:    
    # 팁 정보
    @staticmethod
    async def crud_tips_by_t_id(db:AsyncSession, t_id:int) -> Tip | None:
        result = await db.execute(select(Tip).filter(Tip.t_id == t_id))
        return result.scalars().first()


    # 팁 목록
    @staticmethod
    async def crud_tips_list(db: AsyncSession,
                            t_age: Optional[int] = None,
                            skip: int = 0, 
                            limit: int = 10) -> list[Tip]:

        query = select(Tip).order_by(Tip.t_id)
        
        if t_age is not None:
            query = query.filter(Tip.t_age == t_age)
            
        query = query.offset(skip).limit(limit)
        
        result = await db.execute(query)
        return list(result.scalars().all())
        
    