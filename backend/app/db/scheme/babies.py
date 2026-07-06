from pydantic import BaseModel, Field, ConfigDict, field_validator
from datetime import datetime, timezone
from decimal import Decimal


# ==========================
# Create / Update 입력용
# ==========================

class Baby_Base(BaseModel):
    b_name: str
    b_birth: datetime
    b_gender: str
    b_height: Decimal
    b_weight: Decimal
    b_image: str | None = None

    model_config = ConfigDict(from_attributes=True)

    @field_validator("b_name")
    @classmethod
    def validate_name_not_blank(cls, v):
        if not v.strip():
            raise ValueError("이름을 입력해주세요.")
        return v.strip()

    @field_validator("b_birth")
    @classmethod
    def validate_birth_not_future(cls, v):
        now = datetime.now(v.tzinfo) if v.tzinfo else datetime.now()
        if v > now:
            raise ValueError("생년월일은 오늘 이전 날짜여야 합니다.")
        return v

    @field_validator("b_gender")
    @classmethod
    def validate_gender(cls, v):
        # 프론트에서 남/여를 보내는 경우
        if v not in ("남", "여"):
            raise ValueError("성별을 선택해주세요.")
        return v


class Baby_Create(Baby_Base):
    pass


class Baby_Update(BaseModel):
    b_name: str | None = None
    b_birth: datetime | None = None
    b_gender: str | None = None
    b_height: Decimal | None = None
    b_weight: Decimal | None = None
    b_image: str | None = None


# ==========================
# Response용 (validator 없음)
# ==========================

class Baby_Public(BaseModel):
    b_name: str
    b_birth: datetime
    b_gender: str

    model_config = ConfigDict(from_attributes=True)


class Baby_Read(BaseModel):
    b_id: int
    g_id: int

    b_name: str
    b_birth: datetime
    b_gender: str
    b_height: Decimal
    b_weight: Decimal
    b_image: str | None = None

    b_created_at: datetime = Field(
        default_factory=lambda: datetime.now(timezone.utc)
    )

    model_config = ConfigDict(from_attributes=True)