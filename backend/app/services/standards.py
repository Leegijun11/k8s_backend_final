from fastapi import HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from app.db.crud.standards import BabyStandard_Crud
from app.db.scheme.standards import BabyStandard_Read

class BabyStandard_Service:
    
    # 성별/개월수 기반 표준 조회 (모든 에러 핸들링은 여기서 실행)
    @staticmethod
    async def services_standards_get_by_criteria(db: AsyncSession, 
                                                 sex: str, 
                                                 month: int) -> BabyStandard_Read:
        try:
            # CRUD를 호출하여 순수 DB 데이터를 받아옴
            data = await BabyStandard_Crud.crud_standards_find_by_criteria(db, sex, month)
            
            # 1. 데이터가 없을 때의 예외 처리
            if not data:
                raise HTTPException(
                    status_code=status.HTTP_404_NOT_FOUND, 
                    detail="해당하는 개월수/성별의 표준 데이터를 찾을 수 없습니다."
                )
            return data
            
        # Router로 그대로 보낼 HTTPException은 그냥 raise
        except HTTPException:
            raise
            
        # 2. 기타 시스템 및 DB 연동 과정에서 발생한 모든 에러 처리
        except Exception as e:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=f"표준 가이드라인 데이터 조회 실패: {e}"
            )