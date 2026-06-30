from app.db.database import Base

from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy import ForeignKey, String, Text, TIMESTAMP, func, UniqueConstraint
from datetime import datetime
from typing import TYPE_CHECKING, Optional
from app.db.models.forums import Forums

# 순환 참조(Circular Import) 방지를 위한 타입 체킹
if TYPE_CHECKING:
    from app.db.models.users import User

class ForumLike(Base):
    __tablename__ = 'forumlikes'

    # Unique 복합키 제약 조건 설정
    __table_args__ = (
        UniqueConstraint('f_id', 'u_id', name='uq_forum_like_f_id_u_id'),
    )

    # PK 및 FK
    f_l_id: Mapped[int] = mapped_column(primary_key=True)
    
    # 원본 글 삭제 시 좋아요도 자동 삭제되도록 ondelete="CASCADE" 설정
    f_id: Mapped[int] = mapped_column(ForeignKey('forums.f_id', ondelete="CASCADE"), nullable=False)
    u_id: Mapped[int] = mapped_column(ForeignKey('users.u_id'), nullable=False)

    # 관계(Relationship) 설정
    forum: Mapped["Forums"] = relationship("Forums", back_populates="likes")
    user: Mapped["User"] = relationship("User", back_populates="forum_likes")