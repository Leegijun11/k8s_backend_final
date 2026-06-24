from pydantic import BaseModel, Field, ConfigDict
from datetime import datetime,timezone
from typing import Annotated


class Log_Base(BaseModel): 
    l_content : str
    b_id : int

    model_config = ConfigDict(from_attributes=True)


class Log_Create(Log_Base):
    pass


class Log_Update(BaseModel):
    l_content : str | None = None   
 
    
class Log_Read(Log_Base):
    l_id: int
    l_date : datetime = Field(default_factory=lambda: datetime.now(timezone.utc))


