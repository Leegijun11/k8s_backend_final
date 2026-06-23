from app.db.database import Base

from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy import String, TIMESTAMP, func
from typing import Optional, List, TYPE_CHECKING
from datetime import datetime

if TYPE_CHECKING:
    from app.db.models.parents import Parent
    from app.db.models.babies import Baby
    from app.db.models.alarms import Alarm

class User(Base):
    __tablename__ = 'users'

    u_id: Mapped[int] = mapped_column(primary_key=True)
    u_account: Mapped[str] = mapped_column(String(100), nullable=False, unique=True)
    u_pw: Mapped[str] = mapped_column(String(255), nullable=False)
    u_name: Mapped[str] = mapped_column(String(50), nullable=False)
    u_nickname: Mapped[str] = mapped_column(String(100), nullable=False)
    u_email: Mapped[str] = mapped_column(String(100), nullable=False, unique=True)
    u_phone: Mapped[str] = mapped_column(String(50), nullable=False, unique=True)
    u_address: Mapped[str] = mapped_column(String(255), nullable=False)
    u_created_at: Mapped[datetime] = mapped_column(TIMESTAMP, server_default=func.now())
    u_image: Mapped[Optional[str]] = mapped_column(String(255), nullable=True)
    
    refresh_token: Mapped[Optional[str]] = mapped_column(String(255), nullable=True)
    
    subs: Mapped[List["Parent"]] = relationship("Parent", back_populates="user")
    sent_alarms: Mapped[List["Alarm"]] = relationship("Alarm", foreign_keys="[Alarm.send_id]", back_populates="sender")
    received_alarms: Mapped[List["Alarm"]] = relationship("Alarm", foreign_keys="[Alarm.receive_id]",  back_populates="receiver")
    