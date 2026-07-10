from pydantic import BaseModel, ConfigDict
from datetime import datetime
from typing import Optional

class Milestone_Read(BaseModel):
    m_id: int
    m_months: int
    m_category: str
    app_milestone: str

    model_config = ConfigDict(from_attributes=True)


class MilestoneStatus_Read(Milestone_Read):
    bm_id: Optional[int] = None
    is_achieved: bool = False
    m_achieved_date: Optional[datetime] = None
    d_id: Optional[int] = None
