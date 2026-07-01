from pydantic import BaseModel, ConfigDict
from datetime import date
from typing import Optional


class Story_Create(BaseModel):
    b_id: int
    s_name: str | None=None
    start_date: date
    end_date: date


class Story_Update(BaseModel):
    s_name: str


class Story_Read(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    s_id: int
    s_name: str
    b_id: int