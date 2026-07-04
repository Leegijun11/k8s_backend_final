from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from app.db.models.standards import BabyStandard

class BabyStandard_Crud:

    # 데이터베이스 연결 및 쿼리 실행 역할만 수행 (예외 처리는 상위 Service로 위임)
    @staticmethod
    async def crud_standards_find_by_criteria(db: AsyncSession, 
                                              sex: str, 
                                              month: int) -> BabyStandard | None:
        query = (
            select(BabyStandard)
            .where(BabyStandard.sex == sex)
            .where(BabyStandard.month == month)
        )
        result = await db.execute(query)
        return result.scalars().one_or_none()