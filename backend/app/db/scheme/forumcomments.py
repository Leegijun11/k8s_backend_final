from pydantic import BaseModel, ConfigDict
from datetime import datetime
from typing import Optional
from app.db.models.users import User

class ForumComment_Base(BaseModel):
    fc_content: str
    
    model_config = ConfigDict(from_attributes=True)


class ForumComment_Create(ForumComment_Base):
    pass


class ForumComment_Update(BaseModel):
    fc_content: str | None = None
    # u_id: int


class CommentUser_Read(BaseModel):
    u_nickname: str

    model_config = ConfigDict(from_attributes=True)


class ForumComment_Read(ForumComment_Base):
    f_id:int
    fc_id:int
    u_id:int
    fc_like_count: int=0
    is_liked: bool=False
    user: Optional[CommentUser_Read] = None
