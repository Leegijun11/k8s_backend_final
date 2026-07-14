from sqlalchemy import String, ForeignKey
from sqlalchemy.orm import Mapped, mapped_column, relationship
from app.db.database import Base
from typing import TYPE_CHECKING
from sqlalchemy import Text, TIMESTAMP, func
from datetime import datetime

if TYPE_CHECKING:
    from app.db.models.babies import Baby
    from app.db.models.story_pages import Story_Page

class Story(Base):
    __tablename__ = 'stories'

    s_id: Mapped[int] = mapped_column(primary_key=True)
    s_name: Mapped[str] = mapped_column(String(100), nullable=False)
    s_fcover : Mapped[str] = mapped_column(String(255), nullable=False)
    s_bcover : Mapped[str] = mapped_column(String(255), nullable=False)
    s_creator : Mapped[str] = mapped_column(String(100), nullable=False)
    s_date: Mapped[datetime] = mapped_column(TIMESTAMP, server_default=func.now())
    s_comment : Mapped[str] = mapped_column(String(100), nullable=False)
    b_id: Mapped[int] = mapped_column(ForeignKey('babies.b_id', ondelete="CASCADE"), nullable=False)

    baby: Mapped["Baby"] = relationship("Baby", back_populates="stories")
    pages: Mapped[list["Story_Page"]] = relationship("Story_Page", back_populates="story", cascade="all, delete-orphan")