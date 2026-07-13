from pydantic import BaseModel, ConfigDict
from datetime import date
from typing import Optional

class Story_Base(BaseModel):
    s_fcover: str | None = None
    s_bcover: str | None = None
    s_creator: str | None = None
    s_comment: str | None = None


class Story_Create(BaseModel):
    b_id: int
    s_name: str | None=None
    start_date: date
    end_date: date



class Story_Update(Story_Base):
    s_name: str


class Story_Read(Story_Base):
    model_config = ConfigDict(from_attributes=True)

    s_id: int
    s_name: str
    b_id: int