from app.db.database import Base

from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy import ForeignKey, Numeric, TIMESTAMP, func
from decimal import Decimal
from datetime import datetime
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from app.db.models.babies import Baby

class Record(Base):
    __tablename__ = 'records'

    r_id: Mapped[int] = mapped_column(primary_key=True)
    
    r_height: Mapped[Decimal] = mapped_column(Numeric(precision=5, scale=2), nullable=False)
    r_weight: Mapped[Decimal] = mapped_column(Numeric(precision=5, scale=2), nullable=False)
    r_date: Mapped[datetime] = mapped_column(TIMESTAMP, server_default=func.now())
    
    b_id: Mapped[int] = mapped_column(ForeignKey('babies.b_id', ondelete="CASCADE"), nullable=False, unique=True)

    baby: Mapped["Baby"] = relationship("Baby", back_populates="record")
