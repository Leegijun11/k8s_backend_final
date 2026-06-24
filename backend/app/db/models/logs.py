from app.db.database import Base

from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy import String, TIMESTAMP, func, ForeignKey
from datetime import datetime
from typing import Optional, TYPE_CHECKING

if TYPE_CHECKING:
    from app.db.models.babies import Baby

class Log(Base):
    __tablename__ = 'logs'

    l_id: Mapped[int] = mapped_column(primary_key=True)
    l_content: Mapped[str] = mapped_column(String(1000), nullable=False)
    l_date: Mapped[datetime] = mapped_column(TIMESTAMP, server_default=func.now())

    b_id: Mapped[int] = mapped_column(ForeignKey('babies.b_id', ondelete="CASCADE"), nullable=False)
    
    baby: Mapped["Baby"] = relationship("Baby", back_populates="logs")