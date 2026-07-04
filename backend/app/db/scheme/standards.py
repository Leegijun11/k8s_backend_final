from pydantic import BaseModel

# 1. 응답용 스키마 (Read)
class BabyStandard_Read(BaseModel):
    s_id: int
    sex: str
    month: int
    height: float
    weight: float
    bmi: float
    sleep_min: int
    sleep_max: int
    eat_min: int
    eat_max: int
    toilet_min: int
    toilet_max: int

    class Config:
        from_attributes = True