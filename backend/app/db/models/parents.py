from app.db.database import Base

from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy import String, ForeignKey
from typing import TYPE_CHECKING, Optional

if TYPE_CHECKING:
    from app.db.models.users import User
    from app.db.models.care_group import Care_Group
    from app.db.models.babies import Baby

class Parent(Base):
    __tablename__ = 'parents'

    p_id: Mapped[int] = mapped_column(primary_key=True)   
    p_role: Mapped[str] = mapped_column(String(100), nullable=False)
    p_category: Mapped[str] = mapped_column(String(100), nullable=False)
    p_state: Mapped[str] = mapped_column(String(100), nullable=False)

    g_id: Mapped[Optional[int]] = mapped_column(ForeignKey('care_groups.g_id'), nullable=True)
    u_id: Mapped[int] = mapped_column(ForeignKey('users.u_id', ondelete="CASCADE"), nullable=False)
    
    current_b_id: Mapped[Optional[int]] = mapped_column(ForeignKey('babies.b_id', ondelete="SET NULL"), nullable=True)

    care_group: Mapped[Optional["Care_Group"]] = relationship("Care_Group", back_populates="members")
    user: Mapped["User"] = relationship("User", back_populates="subs")
    current_baby: Mapped[Optional["Baby"]] = relationship("Baby")
