from app.db.database import Base
from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy import ForeignKey, String, TIMESTAMP, func, Integer
from datetime import datetime
from typing import TYPE_CHECKING, Optional

if TYPE_CHECKING:
    from app.db.models.users import User
    from app.db.models.forums import Forums
    from app.db.models.forumcommentlikes import ForumCommentLike

class ForumComment(Base):
    __tablename__ = 'forumcomments'

    fc_id: Mapped[int] = mapped_column(primary_key=True)
    f_id: Mapped[int] = mapped_column(ForeignKey('forums.f_id', ondelete="CASCADE"), nullable=False)
    u_id: Mapped[int] = mapped_column(ForeignKey('users.u_id', ondelete="CASCADE"), nullable=False)
    fc_content: Mapped[str] = mapped_column(String(500), nullable=False)

    fc_like_count: Mapped[int] = mapped_column(Integer, default=0, nullable=False)

    forum: Mapped["Forums"] = relationship("Forums", back_populates="comments")
    user: Mapped["User"] = relationship("User", back_populates="forum_comments")


    comment_likes: Mapped[list["ForumCommentLike"]] = relationship("ForumCommentLike", back_populates="comment", cascade="all, delete-orphan")