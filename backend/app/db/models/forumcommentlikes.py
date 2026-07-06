from app.db.database import Base

from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy import ForeignKey, UniqueConstraint
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from app.db.models.users import User
    from app.db.models.forumcomments import ForumComment


class ForumCommentLike(Base):
    __tablename__ = 'forumcommentlikes'

    __table_args__ = (
        UniqueConstraint('fc_id', 'u_id', name='uq_comment_like_fc_id_u_id'),
    )

    fc_l_id: Mapped[int] = mapped_column(primary_key=True)
    
    fc_id: Mapped[int] = mapped_column(ForeignKey('forumcomments.fc_id', ondelete="CASCADE"), nullable=False)
  
    u_id: Mapped[int] = mapped_column(ForeignKey('users.u_id'), nullable=False)

    comment: Mapped["ForumComment"] = relationship("ForumComment", back_populates="comment_likes")
    user: Mapped["User"] = relationship("User", back_populates="forum_comment_likes")