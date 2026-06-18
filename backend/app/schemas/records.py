from pydantic import BaseModel, Field, EmailStr, ConfigDict
from datetime import datetime,timezone
from typing import Annotated
from decimal import Decimal


class Record_Base(BaseModel): 
    r_height: Decimal
    r_weight: Decimal

    model_config = ConfigDict(from_attributes=True)


class Record_Create(BaseModel):
    r_height: Decimal
    r_weight: Decimal
    b_id : int
    
    
class Record_Read(Record_Base):
    r_id: int


