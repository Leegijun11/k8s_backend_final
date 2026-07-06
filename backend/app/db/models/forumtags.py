from app.db.database import Base
from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy import Boolean, ForeignKey
from typing import TYPE_CHECKING
from app.db.models.forums import Forums

if TYPE_CHECKING:
    from app.db.models.forums import Forums

class ForumTag(Base):
    __tablename__ = 'forum_tags'

    ft_id: Mapped[int] = mapped_column(primary_key=True)

    ft_sleep: Mapped[bool] = mapped_column(Boolean, default=False)  # 수면
    ft_food: Mapped[bool] = mapped_column(Boolean, default=False)   # 이유식
    ft_health: Mapped[bool] = mapped_column(Boolean, default=False) # 건강/발진
    ft_play: Mapped[bool] = mapped_column(Boolean, default=False)   # 놀이/장난감
    
    # 어떤 게시글의 카테고리인지 1:1로 묶어주는 역할
    f_id: Mapped[int] = mapped_column(ForeignKey('forums.f_id', ondelete="CASCADE"), unique=True)


    forum: Mapped["Forums"] = relationship("Forums", back_populates="forum_tag")