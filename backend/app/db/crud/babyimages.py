from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import func
from sqlalchemy.future import select
from datetime import datetime
from app.db.models.babyimages import BabyImage 
from app.db.scheme.babyimages import BabyImage_Create, BabyImage_Update


class BabyImage_Crud:
    # 이미지 등록
    @staticmethod
    async def crud_babyimages_create(db:AsyncSession,
                                  babyimage: BabyImage_Create) -> BabyImage:          
        data = babyimage.model_dump()
        db_data=BabyImage(**data)
        db.add(db_data)
        await db.flush()
        return db_data


    # 이미지 목록
    @staticmethod
    async def crud_babyimages_list(db:AsyncSession,
                                   b_id:int,
                                   i_date:datetime) -> list[BabyImage] | None:
        result = await db.execute(select(BabyImage)
                                  .where(BabyImage.b_id == b_id)
                                  .where(func.date(BabyImage.i_date) == func.date(i_date)))
        return list(result.scalars().all())


    # 이미지 수정
    @staticmethod
    async def crud_babyimages_update(db:AsyncSession,
                                     i_id:int,
                                     babyimage:BabyImage_Update) -> BabyImage | None:
        db_data=await db.get(BabyImage, i_id)
        
        if db_data:           
            update_data= babyimage.model_dump(exclude_unset=True)

            for key, value in update_data.items():
                setattr(db_data, key, value)

            await db.flush()
            return db_data
            
        return None
    

    # 이미지 삭제
    @staticmethod
    async def crud_babyimages_del(db:AsyncSession, 
                               i_id:int) -> BabyImage | None:
        db_data = await db.get(BabyImage, i_id)
        if db_data:
            await db.delete(db_data)
            await db.flush()
            return db_data
        return None
  

