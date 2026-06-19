from pydantic import BaseModel, Field, ConfigDict
from datetime import datetime,timezone
from typing import Annotated


class Diary_Base(BaseModel): 
    d_title : str
    d_content : str
    d_label : str
    d_eat: str | None = None
    d_sleep: str | None = None 
    d_toilet: str | None = None 
    d_temp: str | None = None    
    b_id : int

    model_config = ConfigDict(from_attributes=True)


class Diary_Create(Diary_Base):
    pass


class Diary_Update(BaseModel):
    d_title: str | None = None   
    d_content : str | None = None   
    d_label: str | None = None   
    d_eat: str | None = None
    d_sleep: str | None = None 
    d_toilet: str | None = None 
    d_temp: str | None = None    

    
class Diary_Read(Diary_Base):
    d_id: int
    d_date : datetime = Field(default_factory=lambda: datetime.now(timezone.utc))


