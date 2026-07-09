from sqlalchemy.ext.asyncio import AsyncSession
from fastapi import HTTPException, status
from datetime import datetime
from app.db.crud.babyimages import BabyImage_Crud

from app.db.scheme.babyimages import BabyImage_Create, BabyImage_Update, BabyImage_Read


class BabyImage_Service:


    # 이미지 등록
    @staticmethod
    async def services_babyimages_create(db:AsyncSession, 
                                         babyimage:BabyImage_Create) -> BabyImage_Read:
        try:       
            data = await BabyImage_Crud.crud_babyimages_create(db, babyimage)
            
            await db.commit()
            await db.refresh(data)
            return data

        except Exception as e:
            await db.rollback()
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, 
                                detail=f"이미지 등록 실패 :{e}")


    # 이미지 다중 등록
    @staticmethod
    async def services_babyimages_multi_create(db: AsyncSession,
                                               babyimages: list[BabyImage_Create]) -> list[BabyImage_Read]:
        try:
            created_images = []

            for img in babyimages:
                data = await BabyImage_Crud.crud_babyimages_create(db, img)
                created_images.append(data)
            
            await db.commit()

            for img in created_images:
                await db.refresh(img)
            
            return created_images
        
        except Exception as e:
            await db.rollback()
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, 
                                detail=f"다중 등록 실패: {e}")


    # 이미지 목록
    @staticmethod
    async def services_babyimages_list(db: AsyncSession,
                                       b_id:int,
                                       i_date: datetime) -> list[BabyImage_Read]:
        data = await BabyImage_Crud.crud_babyimages_list(db, b_id, i_date)

        if not data:
            return []
        
        return data
    

    # 이미지 업데이트
    @staticmethod
    async def services_babyimages_update(db:AsyncSession,
                                         i_id:int,
                                         babyimage:BabyImage_Update) -> BabyImage_Read:
        try :
            update=await BabyImage_Crud.crud_babyimages_update(db, i_id, babyimage)
            
            if not update:
                raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, 
                                    detail="수정할 이미지가 없습니다")
            
            await db.commit()
            await db.refresh(update)

            return update
        
        except HTTPException:
            await db.rollback()
            raise

        except Exception as e:
            await db.rollback()
            raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, 
                                detail=f"이미지 수정 실패 :{e}")


    # 이미지 삭제
    @staticmethod
    async def services_babyimages_del(db: AsyncSession, 
                                      i_id: int) -> dict:
        try: 
            delete_data = await BabyImage_Crud.crud_babyimages_del(db, i_id)
        
            if not delete_data:
                raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, 
                                    detail='삭제할 이미지가 없습니다')

            await db.commit()
            return {'message':'이미지 삭제'}
        
        except HTTPException:
            await db.rollback()
            raise

        except Exception as e:
            await db.rollback()
            raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, 
                                detail=f"이미지 삭제 실패 :{e}")
    

    # 다중 이미지 삭제
    @staticmethod
    async def services_babyimages_multi_del(db: AsyncSession, 
                                            i_ids: list[int]) -> None:
        try:
            for i_id in i_ids:
                delete_data = await BabyImage_Crud.crud_babyimages_del(db, i_id)
                if not delete_data:
                    raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,
                                        detail=f"삭제할 이미지를 찾을 수 없습니다.")
                
            await db.commit()

        except HTTPException:
            await db.rollback()
            raise

        except Exception as e:
            await db.rollback()
            raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, 
                                detail=f"다중 삭제 실패: {e}")

    
    #갤러리용(전체 사진 목록)
    @staticmethod
    async def services_babyimages_list_all(db: AsyncSession, b_id: int, year: int, month: int) -> list[BabyImage_Read]:
        try:
            data = await BabyImage_Crud.crud_babyimages_list_all(db, b_id, year, month)
            return [BabyImage_Read.model_validate(item) for item in data]
        
        except HTTPException:
            await db.rollback()
            raise

        except Exception as e:
            raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=f"월별 사진 목록 조회 실패: {e}")