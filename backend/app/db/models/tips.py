from sqlalchemy import String
from sqlalchemy.orm import Mapped, mapped_column
from app.db.database import Base
from typing import TYPE_CHECKING

class Tip(Base):
    __tablename__ = 'tips'

    t_id: Mapped[int] = mapped_column(primary_key=True)
    t_title: Mapped[str] = mapped_column(String(100), nullable=False)
    t_age: Mapped[int] = mapped_column(nullable=False)
    t_content: Mapped[str] = mapped_column(String(255), nullable=False)
