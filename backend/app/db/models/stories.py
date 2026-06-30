from sqlalchemy import String, ForeignKey
from sqlalchemy.orm import Mapped, mapped_column, relationship
from app.db.database import Base
from typing import TYPE_CHECKING
from sqlalchemy import Text
if TYPE_CHECKING:
    from app.db.models.babies import Baby


class Story(Base):
    __tablename__ = 'stories'

    s_id: Mapped[int] = mapped_column(primary_key=True)
    s_name: Mapped[str] = mapped_column(String(100), nullable=False)
    b_id: Mapped[int] = mapped_column(ForeignKey('babies.b_id', ondelete="CASCADE"), nullable=False)
    s_content: Mapped[str] = mapped_column(Text, nullable=True)

    baby: Mapped["Baby"] = relationship("Baby", back_populates="stories")