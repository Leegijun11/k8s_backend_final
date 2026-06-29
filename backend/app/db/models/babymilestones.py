from sqlalchemy import Integer, ForeignKey, Boolean, TIMESTAMP, func
from sqlalchemy.orm import Mapped, mapped_column, relationship
from app.db.database import Base
from datetime import datetime
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from app.db.models.babies import Baby
    from app.db.models.milestones import Milestone

class BabyMilestone(Base):
    __tablename__ = 'baby_milestones'

    bm_id: Mapped[int] = mapped_column(primary_key=True)
    
    # 아기 테이블 참조
    b_id: Mapped[int] = mapped_column(ForeignKey('babies.b_id', ondelete="CASCADE"), nullable=False)
    # 마일스톤 테이블 참조
    m_id: Mapped[int] = mapped_column(ForeignKey('milestones.m_id', ondelete="CASCADE"), nullable=False)
    
    m_achieved: Mapped[bool] = mapped_column(Boolean, default=False)
    m_achieved_date: Mapped[datetime] = mapped_column(TIMESTAMP, nullable=True)

    # 관계 설정
    baby: Mapped["Baby"] = relationship("Baby", back_populates="baby_milestones")
    milestone: Mapped["Milestone"] = relationship("Milestone", back_populates="baby_milestones")