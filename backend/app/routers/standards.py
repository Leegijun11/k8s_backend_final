from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from app.db.database import get_db
from app.db.scheme.standards import BabyStandard_Read
from app.services.standards import BabyStandard_Service

router = APIRouter(prefix='/standards', tags=['BabyStandard'])

# GET 성별 및 개월수 기준 표준 가이드라인 조회
@router.get('', response_model=BabyStandard_Read)
async def router_standards_get(sex: str, 
                               month: int, 
                               db: AsyncSession = Depends(get_db)):
    # 1. 간단한 파라미터 유효성 검사
    if sex not in ['M', 'F']:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="성별은 'M' 또는 'F'여야 합니다.")
    if not (0 <= month <= 60):
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="개월수는 0에서 60 사이여야 합니다.")
        
    # 2. 오직 Service만 호출하고 리턴받음
    return await BabyStandard_Service.services_standards_get_by_criteria(db, sex, month)