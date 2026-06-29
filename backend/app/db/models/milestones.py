from sqlalchemy import String, Integer
from sqlalchemy.orm import Mapped, mapped_column, relationship
from app.db.database import Base
from typing import List, TYPE_CHECKING

if TYPE_CHECKING:
    from app.db.models.babymilestones import BabyMilestone

class Milestone(Base):
    __tablename__ = 'milestones'

    m_id: Mapped[int] = mapped_column(primary_key=True)
    m_months: Mapped[int] = mapped_column(Integer, nullable=False)
    m_category: Mapped[str] = mapped_column(String(50), nullable=False)
    app_milestone: Mapped[str] = mapped_column(String(255), nullable=False) # 한글 문구

    # BabyMilestone과의 관계
    baby_milestones: Mapped[List["BabyMilestone"]] = relationship("BabyMilestone", back_populates="milestone")