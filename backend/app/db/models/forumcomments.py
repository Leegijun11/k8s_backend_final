from app.db.database import Base
from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy import ForeignKey, String, TIMESTAMP, func
from datetime import datetime
from typing import TYPE_CHECKING, Optional
from app.db.models.forumcommentlikes import ForumCommentLike

if TYPE_CHECKING:
    from app.db.models.users import User
    from app.db.models.forums import Forum
    from app.db.models.forumcommentlikes import ForumCommentLike

class ForumComment(Base):
    __tablename__ = 'forumcomments'

    fc_id: Mapped[int] = mapped_column(primary_key=True)
    f_id: Mapped[int] = mapped_column(ForeignKey('forums.f_id', ondelete="CASCADE"), nullable=False)    u_id: Mapped[int] = mapped_column(ForeignKey('users.u_id'), nullable=False)
    u_id: Mapped[int] = mapped_column(ForeignKey('users.u_id'), nullable=False)
    fc_content: Mapped[str] = mapped_column(String(500), nullable=False)

    forum: Mapped["Forum"] = relationship("Forum", back_populates="comments")
    user: Mapped["User"] = relationship("User", back_populates="forum_comments")
    comment_likes: Mapped[list["ForumCommentLike"]] = relationship("ForumCommentLike", back_populates="comment", cascade="all, delete-orphan")