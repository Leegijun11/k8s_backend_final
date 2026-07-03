from pydantic import BaseModel, ConfigDict
from datetime import datetime

class ForumComment_Base(BaseModel):
    fc_content: str
    
    model_config = ConfigDict(from_attributes=True)


class ForumComment_Create(ForumComment_Base):
    f_id: int
    u_id: int


class Forum_Update(BaseModel):
    fc_content: str | None = None


class Forum_Read(ForumComment_Base):
    f_id:int
    fc_id:int
    u_id:int
