from pydantic import BaseModel, Field, EmailStr, ConfigDict
from datetime import datetime,timezone
from typing import Annotated


class BabyCharacter_Base(BaseModel):
    c_curiosity: bool 
    c_active: bool
    c_shy: bool
    c_eater: bool
    c_sleepy: bool
    c_charm: bool

    model_config = ConfigDict(from_attributes=True)


class BabyCharacter_Create(BabyCharacter_Base):
    b_id : int


class BabyCharacter_Update(BaseModel):
    c_curiosity : bool | None = None 
    c_active: bool | None = None 
    c_shy: bool | None = None 
    c_eater: bool | None = None 
    c_sleepy: bool | None = None 
    c_charm: bool | None = None 

    
class BabyCharacter_Read(BabyCharacter_Base):
    c_id: int
    b_id: int


