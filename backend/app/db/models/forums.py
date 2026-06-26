from app.db.database import Base

from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy import ForeignKey, String, Text, TIMESTAMP, func, UniqueConstraint
from datetime import datetime
from typing import TYPE_CHECKING, Optional
from app.db.models.forumlikes import ForumLike

# 순환 참조(Circular Import) 방지를 위한 타입 체킹
if TYPE_CHECKING:
    from app.db.models.users import User  


# 1. 게시글 테이블 (Forums)
class Forums(Base):
    __tablename__ = 'forums'

    # PK 및 기본 정보
    f_id: Mapped[int] = mapped_column(primary_key=True)
    u_id: Mapped[int] = mapped_column(ForeignKey('users.u_id'), nullable=False)
    
    # 필수 텍스트 필드
    f_title: Mapped[str] = mapped_column(String(255), nullable=False)
    f_content: Mapped[str] = mapped_column(Text, nullable=False)
    
    # 선택 필드 (Null 허용이므로 Optional 사용)
    f_image: Mapped[Optional[str]] = mapped_column(String(255), nullable=True)
    f_tags: Mapped[Optional[str]] = mapped_column(String(255), nullable=True)
    
    # 시간 필드 (작성일시는 기본값 삽입, 수정일시는 업데이트 시 자동 갱신)
    f_created_at: Mapped[datetime] = mapped_column(TIMESTAMP, server_default=func.now(), nullable=False)
    f_updated_at: Mapped[Optional[datetime]] = mapped_column(TIMESTAMP, onupdate=func.now(), nullable=True)

    # 관계(Relationship) 설정
    user: Mapped["User"] = relationship("User", back_populates="forums")
    likes: Mapped[list["ForumLike"]] = relationship("ForumLike", back_populates="forum", cascade="all, delete-orphan")