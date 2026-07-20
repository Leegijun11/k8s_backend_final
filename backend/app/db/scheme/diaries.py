from pydantic import BaseModel, ConfigDict, Field
from datetime import datetime
from typing import Optional


class Diary_Create(BaseModel):
    d_title: Optional[str] = None
    d_content: Optional[str] = None
    d_label: Optional[str] = None
    d_image: Optional[str] = None
    d_eat: Optional[str] = None
    d_sleep: Optional[str] = None
    d_toilet: Optional[str] = None
    d_temp: Optional[str] = None
    d_date: datetime = Field(default_factory=datetime.now)
    b_id: int
    original_text: Optional[str] = None

class Diary_Read(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    d_id: int
    d_title: str
    d_content: str
    d_label: Optional[str] = None
    d_date: datetime
    d_image: Optional[str] = None
    d_eat: Optional[str] = None
    d_sleep: Optional[str] = None
    d_toilet: Optional[str] = None
    d_temp: Optional[str] = None
    b_id: int

class Diary_List_Item(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    d_id: int
    d_title: str
    d_content: str
    d_label: str
    d_date: datetime
    d_image: Optional[str] = None
    d_eat: Optional[str] = None
    d_sleep: Optional[str] = None
    d_toilet: Optional[str] = None
    d_temp: Optional[str] = None



class Diary_Detail(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    d_title: str
    d_content: str
    d_label: str
    d_date: datetime
    d_image: Optional[str] = None
    d_eat: Optional[str] = None
    d_sleep: Optional[str] = None
    d_toilet: Optional[str] = None
    d_temp: Optional[str] = None

class Diary_Update(BaseModel):
    d_title: Optional[str] = None
    d_content: Optional[str] = None
    d_label: Optional[str] = None
    d_eat: Optional[str] = None
    d_sleep: Optional[str] = None
    d_toilet: Optional[str] = None
    d_temp: Optional[str] = None
