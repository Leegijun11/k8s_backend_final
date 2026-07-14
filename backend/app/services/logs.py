from sqlalchemy.ext.asyncio import AsyncSession
from fastapi import HTTPException, status
from datetime import datetime
from app.db.crud.logs import Log_Crud

from app.db.scheme.logs import Log_Create, Log_Update, Log_Read


class Log_Service:
    # 기록 작성 & 수정
    @staticmethod
    async def services_logs_create_update(db:AsyncSession,
                                          log:Log_Create) -> Log_Read:
        try:
            data = await Log_Crud.crud_logs_create(db, log)
            await db.commit()
            await db.refresh(data)
            return data
        
        except HTTPException:
            await db.rollback()
            raise
        
        except Exception as e:
            await db.rollback()
            raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                                detail=f"기록 저장 실패: {e}")


    # 기록 상세
    @staticmethod
    async def services_logs_detail(db: AsyncSession,
                                   l_id:int) -> Log_Read | None:
        return await Log_Crud.crud_logs_detail(db, l_id)

    # 기록 삭제
    @staticmethod
    async def services_logs_del(db: AsyncSession,
                                l_id: int) -> dict:
        try: 
            delete_data = await Log_Crud.crud_logs_del(db, l_id)
        
            if not delete_data:
                raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, 
                                    detail='삭제할 기록이 없습니다')

            await db.commit()
            return {'message':'기록 삭제'}
        
        except HTTPException:
            await db.rollback()
            raise

        except Exception as e:
            await db.rollback()
            raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, 
                                detail=f"기록 삭제 실패 :{e}")
        
    # 기록 목록
    @staticmethod
    async def services_logs_list(db: AsyncSession, b_id: int):
        return await Log_Crud.crud_logs_list(db, b_id)
    
