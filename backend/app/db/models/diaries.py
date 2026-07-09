from app.db.database import Base
from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy import String, TIMESTAMP, func, ForeignKey
from datetime import datetime
from typing import Optional, TYPE_CHECKING

if TYPE_CHECKING:
    from app.db.models.babies import Baby
    from app.db.models.babymilestones import BabyMilestone

class Diary(Base):
    __tablename__ = 'diaries'

    d_id: Mapped[int] = mapped_column(primary_key=True)
    d_title: Mapped[str] = mapped_column(String(100), nullable=False)
    d_content: Mapped[str] = mapped_column(String(255), nullable=False)
    d_label: Mapped[str] = mapped_column(String(100),nullable=False)
    d_date: Mapped[datetime] = mapped_column(TIMESTAMP, server_default=func.now())
    d_image: Mapped[Optional[str]] = mapped_column(String(255), nullable=True)
    
    d_eat: Mapped[Optional[str]] = mapped_column(String(100), nullable=True)
    d_sleep: Mapped[Optional[str]] = mapped_column(String(100), nullable=True)
    d_toilet: Mapped[Optional[str]] = mapped_column(String(100), nullable=True)
    d_temp: Mapped[Optional[str]] = mapped_column(String(100), nullable=True)
    
    b_id: Mapped[int] = mapped_column(ForeignKey('babies.b_id', ondelete="CASCADE"), nullable=False)
    
    baby: Mapped["Baby"] = relationship("Baby", back_populates="diaries")
    milestone: Mapped["BabyMilestone"] = relationship(
        "BabyMilestone", 
        back_populates="diary", 
        cascade="all, delete-orphan",
        passive_deletes=True
)