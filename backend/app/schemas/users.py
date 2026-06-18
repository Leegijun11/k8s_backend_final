from pydantic import BaseModel, Field, EmailStr, ConfigDict
from datetime import datetime,timezone
from typing import Annotated


class User_Base(BaseModel): 
    u_account: str
    u_email: EmailStr
    u_phone: str

    model_config = ConfigDict(from_attributes=True)


class User_Create(BaseModel):
    u_account: str
    u_pw: Annotated[str, Field(max_length=72)]
    u_name: str
    u_nickname : str
    u_email: EmailStr
    u_phone: str


class User_Login(BaseModel):
    u_account: str
    u_pw: Annotated[str, Field(max_length=72)]


class User_Update(BaseModel):
    u_pw: Annotated[str | None, Field(max_length=72, default=None)] = None 
    u_name: str | None = None   
    u_nickname : str | None = None   
    u_email: EmailStr | None = None   
    u_phone: str | None = None   


class User_Public(User_Base):
    u_name: str
    u_nickname : str
    
    
class User_Read(User_Public):
    u_id: int
    signup_date: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))


