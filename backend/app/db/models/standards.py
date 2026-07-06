from app.db.database import Base
from sqlalchemy.orm import Mapped, mapped_column
from sqlalchemy import String

class BabyStandard(Base):
    __tablename__ = 'baby_standards'

    # 1. 고유 PK (복합키 대신 깔끔하게 자동 증가 컬럼 사용)
    s_id: Mapped[int] = mapped_column(primary_key=True)
    
    # 2. 기준 분류 키 (성별 'M'/'F', 개월 수 0~60)
    sex: Mapped[str] = mapped_column(String(1), nullable=False)  # 'M' 또는 'F'
    month: Mapped[int] = mapped_column(nullable=False)
    
    # 3. 신체 성장 표준 지표 (WHO 기준)
    height: Mapped[float] = mapped_column(nullable=False)
    weight: Mapped[float] = mapped_column(nullable=False)
    bmi: Mapped[float] = mapped_column(nullable=False)
    
    # 4. 일일 권장 활동 범위 (수면, 식사, 배변)
    sleep_min: Mapped[int] = mapped_column(nullable=False)
    sleep_max: Mapped[int] = mapped_column(nullable=False)
    
    eat_min: Mapped[int] = mapped_column(nullable=False)
    eat_max: Mapped[int] = mapped_column(nullable=False)
    
    toilet_min: Mapped[int] = mapped_column(nullable=False)
    toilet_max: Mapped[int] = mapped_column(nullable=False)