from app.db.database import Base
from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy import String, ForeignKey
from typing import List, TYPE_CHECKING

if TYPE_CHECKING:
    from app.db.models.parents import Parent
    from app.db.models.babies import Baby
    from app.db.models.alarms import Alarm

class Care_Group(Base):
    __tablename__ = 'care_groups'

    g_id: Mapped[int] = mapped_column(primary_key=True)
    creator_id: Mapped[int] = mapped_column(ForeignKey('users.u_id'), nullable=False)
    
    members: Mapped[List["Parent"]] = relationship("Parent", back_populates="care_group", cascade="all, delete-orphan")
    babies: Mapped[List["Baby"]] = relationship("Baby", back_populates="care_group", cascade="all, delete-orphan")
    alarms: Mapped[List["Alarm"]] = relationship("Alarm", back_populates="care_group", cascade="all, delete-orphan")