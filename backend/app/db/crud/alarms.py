from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from app.db.models.alarms import Alarm 
from app.db.scheme.alarms import Alarm_Create


class Alarm_Crud:
    # 알람 생성
    @staticmethod
    async def crud_alarms_create(db:AsyncSession,
                                 alarm: Alarm_Create) -> Alarm:          
        data = alarm.model_dump()
        db_data=Alarm(**data)
        db.add(db_data)
        await db.flush()
        return db_data


    # 알람 목록
    @staticmethod
    async def crud_alarms_list(db:AsyncSession,
                               receive_id:int) -> list[Alarm] | None:
        result = await db.execute(select(Alarm)
                                  .where(Alarm.receive_id == receive_id))
        return list(result.scalars().all())


    # 알람 삭제
    @staticmethod
    async def crud_alarms_del(db:AsyncSession, 
                               a_id:int) -> Alarm | None:
        db_data = await db.get(Alarm, a_id)
        if db_data:
            await db.delete(db_data)
            await db.flush()
            return db_data
        return None


    # 수신자의 알람 전체 삭제 / 삭제 개수 반환
    @staticmethod
    async def crud_alarms_all_del(db:AsyncSession, 
                               receive_id:int) -> int | None:
        query = select(Alarm).where(Alarm.receive_id == receive_id)
        result = await db.execute(query)
        
        db_data_list = result.scalars().all()

        if db_data_list:
            for db_data in db_data_list:
                await db.delete(db_data)
                
            await db.flush()

            return len(db_data_list)
                
        return None
