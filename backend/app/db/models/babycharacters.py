from app.db.database import Base

from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy import Boolean, ForeignKey
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from app.db.models.babies import Baby

class BabyCharacter(Base):
    __tablename__ = 'babycharacters'

    c_id: Mapped[int] = mapped_column(primary_key=True)
    
    c_curiosity: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False)
    c_active: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False)
    c_shy: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False)
    c_eater: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False)
    c_sleepy: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False)
    c_charm: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False)
    
    b_id: Mapped[int] = mapped_column(ForeignKey('babies.b_id', ondelete="CASCADE"), nullable=False, unique=True)

    baby: Mapped["Baby"] = relationship("Baby", back_populates="character")
