from pydantic import BaseModel, Field, EmailStr, ConfigDict, field_validator
from datetime import datetime,timezone
from typing import Annotated, Optional
import re

PHONE_PATTERN = r'^010\d{7,8}$'
ACCOUNT_PATTERN = r'^(?=.*[a-zA-Z])[a-zA-Z\d]{4,20}$'

class User_Base(BaseModel): 
    u_account: str
    u_email: EmailStr
    u_phone: str
    u_address: str
    model_config = ConfigDict(from_attributes=True)


class User_Create(BaseModel):
    u_account: Annotated[str, Field(min_length=4, max_length=20)]
    u_pw: Annotated[str, Field(min_length=8, max_length=72)]
    u_name: Annotated[str, Field(min_length=1, max_length=50)]
    u_nickname: Annotated[str, Field(min_length=1, max_length=100)]
    u_email: EmailStr
    u_phone: Annotated[str, Field(min_length=1)]
    u_address: Annotated[str, Field(min_length=1, max_length=255)]
    u_image: Optional[str] = None

    @field_validator('u_account')
    @classmethod
    def validate_account(cls, v):
        if not re.match(ACCOUNT_PATTERN, v):
            raise ValueError('아이디는 영문 포함 4~20자 (영문+숫자)여야 합니다.')
        return v

    @field_validator('u_phone')
    @classmethod
    def validate_phone(cls, v):
        if not re.match(PHONE_PATTERN, v):
            raise ValueError('전화번호 형식이 올바르지 않습니다. (예: 010XXXXXXXX)')
        return v

    @field_validator('u_name', 'u_nickname', 'u_address')
    @classmethod
    def not_blank(cls, v):
        if not v.strip():
            raise ValueError('공백만 입력할 수 없습니다.')
        return v.strip()

    @field_validator('u_pw')
    @classmethod
    def validate_pw(cls, v):
        if not re.search(r'\d', v) or not re.search(r'[@$!%*#?&]', v):
            raise ValueError('비밀번호는 숫자와 특수문자를 포함해야 합니다.')
        return v
    
class User_Login(BaseModel):
    u_account: str
    u_pw: Annotated[str, Field(max_length=72)]


class User_pw(BaseModel):
    u_pw: Annotated[str, Field(max_length=72)]


class User_Update(BaseModel):
    u_pw: Annotated[str | None, Field(max_length=72)] = None
    u_name: Annotated[str | None, Field(min_length=1, max_length=50)] = None
    u_nickname: Annotated[str | None, Field(min_length=1, max_length=100)] = None
    u_email: EmailStr | None = None
    u_phone: Annotated[str | None, Field(min_length=1)] = None
    u_address: Annotated[str | None, Field(min_length=1, max_length=255)] = None
    u_image: str | None = None

    @field_validator('u_pw')
    @classmethod
    def validate_pw(cls, v):
        if v is None:
            return v
        if len(v) < 8:
            raise ValueError('비밀번호는 8자 이상이어야 합니다.')
        if not re.search(r'\d', v) or not re.search(r'[@$!%*#?&]', v):
            raise ValueError('비밀번호는 숫자와 특수문자를 포함해야 합니다.')
        return v

    @field_validator('u_phone')
    @classmethod
    def validate_phone(cls, v):
        if v is not None and not re.match(PHONE_PATTERN, v):
            raise ValueError('전화번호 형식이 올바르지 않습니다. (예: 010XXXXXXXX)')
        return v

    @field_validator('u_name', 'u_nickname', 'u_address')
    @classmethod
    def not_blank(cls, v):
        if v is not None and not v.strip():
            raise ValueError('공백만 입력할 수 없습니다.')
        return v.strip() if v is not None else v
    
class User_Read(User_Base):
    u_id: int
    u_name: str
    u_nickname : str
    u_address: str
    u_image: Optional[str] = None
    u_created_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))

class User_Public(BaseModel):
    u_account: str
    u_nickname: str
    u_created_at: datetime

    model_config = ConfigDict(from_attributes=True)


# #User_Read user주머니를 담게해줌
# class User_Me_Response(BaseModel):
#     user: User_Read


#     model_config=ConfigDict(from_attributes=True)


