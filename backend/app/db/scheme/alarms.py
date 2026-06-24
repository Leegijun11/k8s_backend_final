from pydantic import BaseModel, Field, EmailStr, ConfigDict
from datetime import datetime,timezone
from typing import Annotated


class Alarm_Base(BaseModel): 
    send_id: int
    receive_id: int
    g_id: int

    model_config = ConfigDict(from_attributes=True)


class Alarm_Create(Alarm_Base):
    pass

    
class Alarm_Read(Alarm_Base):
    a_id: int
    a_created_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))