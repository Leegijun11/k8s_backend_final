from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import func
from sqlalchemy.future import select
from datetime import date
from app.db.models.logs import Log 
from app.db.scheme.logs import Log_Create, Log_Update


class Log_Crud:
    # 기록 생성
    @staticmethod
    async def crud_logs_create(db:AsyncSession,
                               log: Log_Create) -> Log:          
        data = log.model_dump()
        db_data=Log(**data)
        db.add(db_data)
        await db.flush()
        return db_data


    # 오늘 기록 확인
    @staticmethod
    async def crud_logs_detail(db: AsyncSession,
                               l_id: int) -> Log:        
        result = await db.execute(select(Log).where(Log.l_id == l_id))
        return result.scalars().one_or_none()
    

    # 오늘 기록 여부 확인
    @staticmethod
    async def crud_logs_find_date_b_id(db: AsyncSession,
                                       b_id: int) -> Log | None:
        query=(select(Log)
               .where(Log.b_id == b_id)
               .where(func.date(Log.l_date) == func.date(date.today())))
        
        result = await db.execute(query)
        return result.scalars().one_or_none()
        

    # 기록 수정
    @staticmethod
    async def crud_logs_update(db:AsyncSession,
                               l_id:int,
                               log:Log_Update) -> Log | None:
        db_data=await db.get(Log, l_id)
        
        if db_data:           
            update_data= log.model_dump(exclude_unset=True)

            for key, value in update_data.items():
                setattr(db_data, key, value)

            await db.flush()
            return db_data
            
        return None
    

    # 기록 삭제
    @staticmethod
    async def crud_logs_del(db:AsyncSession,
                            l_id:int) -> Log | None:
        db_data = await db.get(Log, l_id)
        if db_data:
            await db.delete(db_data)
            await db.flush()
            return db_data
        return None
    
    #기록 목록
    @staticmethod
    async def crud_logs_list(db: AsyncSession, b_id: int) -> list[Log]:
        query = (select(Log)
                 .where(Log.b_id == b_id)
                 .order_by(Log.l_date.desc()))
        
        result = await db.execute(query)
        return list(result.scalars().all())

