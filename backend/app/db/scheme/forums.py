from pydantic import BaseModel, ConfigDict
from datetime import datetime
from typing import List


class Forum_Base(BaseModel):
    f_title: str
    f_content: str
    f_image: str | None = None
    f_tags: str | None = None

    model_config = ConfigDict(from_attributes=True)


class Forum_Create(Forum_Base):
    pass 


class Forum_Update(BaseModel):
    f_title: str | None = None
    f_content: str | None = None
    f_image: str | None = None
    f_tags: str | None = None


class Forum_Read(Forum_Base):
    f_id: int
    u_id: int
    f_created_at: datetime
    f_updated_at: datetime | None = None




