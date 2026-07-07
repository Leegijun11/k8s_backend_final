from app.db.database import Base

from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy import ForeignKey, String, Text, TIMESTAMP, func, Boolean, Integer
from datetime import datetime
from typing import TYPE_CHECKING, Optional, List

# 순환 참조(Circular Import) 방지를 위한 타입 체킹
if TYPE_CHECKING:
    from app.db.models.users import User
    from app.db.models.forumlikes import ForumLike
    from app.db.models.forumtags import ForumTag
    from app.db.models.babies import Baby
    from app.db.models.forumcomments import ForumComment


# 1. 게시글 테이블 (Forums)
class Forums(Base):
    __tablename__ = 'forums'


    f_id: Mapped[int] = mapped_column(primary_key=True)
    u_id: Mapped[int] = mapped_column(ForeignKey('users.u_id'), nullable=False)
    
    f_title: Mapped[str] = mapped_column(String(255), nullable=False)
    f_content: Mapped[str] = mapped_column(Text, nullable=False)

    f_image: Mapped[Optional[str]] = mapped_column(String(500), nullable=True) # 이미지 URL 길이를 고려해 500 권장
    
    f_like_count: Mapped[int] = mapped_column(Integer, default=0, nullable=False)

    f_created_at: Mapped[datetime] = mapped_column(TIMESTAMP, server_default=func.now(), nullable=False)
    f_updated_at: Mapped[Optional[datetime]] = mapped_column(TIMESTAMP, onupdate=func.now(), nullable=True)

    user: Mapped["User"] = relationship("User", back_populates="forums")
    likes: Mapped[list["ForumLike"]] = relationship("ForumLike", back_populates="forum", cascade="all, delete-orphan")

    forum_tag: Mapped["ForumTag"] = relationship("ForumTag", back_populates="forum", cascade="all, delete-orphan")

    b_id: Mapped[Optional[int]]=mapped_column(ForeignKey('babies.b_id', ondelete="SET NULL"), nullable=True)

    baby: Mapped[Optional["Baby"]] = relationship("Baby", back_populates="forums")
    forum_likes: Mapped[List["ForumLike"]] = relationship("ForumLike", back_populates="forum", cascade="all, delete-orphan", overlaps="likes")

    comments: Mapped[list["ForumComment"]] = relationship("ForumComment", back_populates="forum", cascade="all, delete-orphan")