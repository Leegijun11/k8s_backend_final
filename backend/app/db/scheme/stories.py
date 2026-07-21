from pydantic import BaseModel, ConfigDict
from datetime import date
from typing import Optional

class Story_Base(BaseModel):
    s_fcover: str = "없음"
    s_bcover: str = "없음"
    s_creator: str = "없음"
    s_comment: str = "없음"


class Story_Create(Story_Base):
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