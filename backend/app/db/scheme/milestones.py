from pydantic import BaseModel
from datetime import datetime
from typing import Optional

class Milestone_Read(BaseModel):
    m_id: int
    m_months: int
    m_category: str
    app_milestone: str
    is_achieved: bool = False  # 조인 시 결합될 필드

    class Config:
        from_attributes = True

class BabyMilestone_Update(BaseModel):
    b_id: int
    milestone_id: int
    is_achieved: bool