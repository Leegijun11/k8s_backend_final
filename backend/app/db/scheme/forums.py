from pydantic import BaseModel, ConfigDict
from datetime import datetime
from typing import List, Optional
from app.db.scheme.forumtags import ForumTag_Create, ForumTag_Update, ForumTag_Read
from app.db.scheme.users import User_Read

class Forum_Base(BaseModel):
    f_title: str
    f_content: str
    f_image: Optional[str] = None

    model_config = ConfigDict(from_attributes=True)


class Forum_Create(Forum_Base):
    b_id: int| None = None
    forum_tag: ForumTag_Create


class Forum_Update(BaseModel):
    f_title: str | None = None
    f_content: str | None = None
    f_image: str | None = None
    forum_tag: Optional[ForumTag_Update] = None
    

class Forum_Read(Forum_Base):
    f_id: int
    u_id: int
    b_id: int | None = None
    f_like_count: int
    f_created_at: datetime
    f_updated_at: datetime | None = None

    forum_tag: Optional[ForumTag_Update] = None

    user: User_Read


