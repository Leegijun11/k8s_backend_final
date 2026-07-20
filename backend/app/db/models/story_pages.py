from sqlalchemy import String, ForeignKey
from sqlalchemy.orm import Mapped, mapped_column, relationship
from app.db.database import Base
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from app.db.models.stories import Story


class Story_Page(Base):
    __tablename__ = 'story_pages'

    sp_id: Mapped[int] = mapped_column(primary_key=True)
    sp_content: Mapped[str] = mapped_column(String(500), nullable=False)
    sp_image: Mapped[str | None] = mapped_column(String(500), nullable=False)
    sp_num: Mapped[int] = mapped_column(nullable=False)
    s_id: Mapped[int] = mapped_column(ForeignKey('stories.s_id', ondelete="CASCADE"), nullable=False)

    story: Mapped["Story"] = relationship("Story", back_populates="pages")
    