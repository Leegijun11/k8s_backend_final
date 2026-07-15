from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from sqlalchemy import extract
from datetime import datetime
from app.db.models.records import Record 
from app.db.scheme.records import Record_Create, Record_Update


class Record_Crud:
    # 아이 성장 누적기록 등록 (월 단위 upsert)
    @staticmethod
    async def crud_records_create(db: AsyncSession,
                                   record: Record_Create) -> Record:
        data = record.model_dump()

        target_date = data.get("r_date") or datetime.utcnow()
        if isinstance(target_date, str):
            target_date = datetime.fromisoformat(target_date)
        data["r_date"] = target_date

        db_data = Record(**data)
        db.add(db_data)
        await db.flush()
        return db_data


    # 아이 성장 정보 조회
    @staticmethod
    async def crud_records_details(
        db: AsyncSession,
        b_id: int
    ) -> list[Record]:

        result = await db.execute(
            select(Record)
            .where(Record.b_id == b_id)
            .order_by(Record.r_date.asc())
        )

        return list(result.scalars().all())


    # 아이 성장정보 수정
    @staticmethod
    async def crud_records_update(db:AsyncSession,
                                  r_id:int,
                                  record:Record_Update) -> Record | None:
        db_data=await db.get(Record, r_id)
        
        if db_data:           
            update_data= record.model_dump(exclude_unset=True)

            for key, value in update_data.items():
                setattr(db_data, key, value)

            await db.flush()
            return db_data
            
        return None
    

    # 아이 성장정보 삭제
    @staticmethod
    async def crud_records_del(db:AsyncSession, 
                               r_id:int) -> Record | None:
        db_data = await db.get(Record, r_id)
        if db_data:
            await db.delete(db_data)
            await db.flush()
            return db_data
        return None
  

