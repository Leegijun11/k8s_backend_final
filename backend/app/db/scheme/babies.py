from pydantic import BaseModel, Field, EmailStr, ConfigDict
from datetime import datetime,timezone
from typing import Annotated
from decimal import Decimal


class Baby_Base(BaseModel): 
    b_name: str
    b_birth : datetime
    b_gender: str
    b_height: Decimal
    b_weight : Decimal
    b_image : str | None = None 

    model_config = ConfigDict(from_attributes=True)


class Baby_Create(Baby_Base):
    pass


class Baby_Update(BaseModel):
    b_name: str | None = None 
    b_birth : datetime | None = None 
    b_gender: str | None = None 
    b_height: Decimal | None = None 
    b_weight : Decimal | None = None 
    b_image : str | None = None   


class Baby_Public(Baby_Base):
    b_name: str
    b_birth : datetime
    b_gender : str
    
    
class Baby_Read(Baby_Base):
    b_id: int
    g_id : int
    b_created_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    


