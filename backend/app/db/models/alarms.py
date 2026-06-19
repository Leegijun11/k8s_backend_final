from app.db.database import Base

from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy import String, TIMESTAMP, func, ForeignKey
from datetime import datetime
from typing import Optional, TYPE_CHECKING

if TYPE_CHECKING:
    from app.db.models.users import User
    from app.db.models.care_group import Care_Group


class Alarm(Base):
    __tablename__ = 'alarms'

    a_id: Mapped[int] = mapped_column(primary_key=True)
    a_created_at: Mapped[datetime] = mapped_column(TIMESTAMP, server_default=func.now())

    send_id: Mapped[int] = mapped_column(ForeignKey("users.u_id"), nullable=False)
    receive_id: Mapped[int] = mapped_column(ForeignKey("users.u_id"), nullable=False)
    g_id: Mapped[int] = mapped_column(ForeignKey('care_groups.g_id'), nullable=False)
    
    sender: Mapped["User"] = relationship("User", foreign_keys=[send_id], back_populates="sent_alarms")
    receiver: Mapped["User"] = relationship("User", foreign_keys=[receive_id], back_populates="received_alarms")
    care_group: Mapped["Care_Group"] = relationship("Care_Group", back_populates="alarms")