from app.db.database import Base

from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy import String, TIMESTAMP, func, ForeignKey, Boolean, Numeric
from datetime import datetime
from decimal import Decimal
from typing import Optional, List, TYPE_CHECKING

if TYPE_CHECKING:
    from app.db.models.care_group import Care_Group
    from app.db.models.babycharacters import BabyCharacter
    from app.db.models.diaries import Diary
    from app.db.models.records import Record
    from app.db.models.babyimages import BabyImage

class Baby(Base):
    __tablename__ = 'babies'

    b_id: Mapped[int] = mapped_column(primary_key=True)
    b_name: Mapped[str] = mapped_column(String(100), nullable=False)
    b_birth: Mapped[datetime] = mapped_column(TIMESTAMP, nullable=False)
    b_gender: Mapped[str] = mapped_column(String(10), default='남')
    b_height: Mapped[Decimal] = mapped_column(Numeric(precision=5, scale=2), nullable=False)
    b_weight: Mapped[Decimal] = mapped_column(Numeric(precision=5, scale=2), nullable=False)
    
    b_image: Mapped[Optional[str]] = mapped_column(String(255), nullable=True)
    b_created_at: Mapped[datetime] = mapped_column(TIMESTAMP, server_default=func.now())
    
    g_id: Mapped[int] = mapped_column(ForeignKey('care_groups.g_id'), nullable=False)
    
    care_group: Mapped["Care_Group"] = relationship("Care_Group", back_populates="babies")
    character: Mapped[Optional["BabyCharacter"]] = relationship("BabyCharacter", back_populates="baby", cascade="all, delete-orphan")
    diaries: Mapped[List["Diary"]] = relationship("Diary", back_populates="baby", cascade="all, delete-orphan")
    record: Mapped[list["Record"]] = relationship("Record", back_populates="baby", cascade="all, delete-orphan")
    images: Mapped[List["BabyImage"]] = relationship("BabyImage", back_populates="baby", cascade="all, delete-orphan")
