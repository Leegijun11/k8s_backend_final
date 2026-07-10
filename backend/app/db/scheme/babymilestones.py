from pydantic import BaseModel, Field, ConfigDict
from datetime import datetime,timezone
from typing import Optional

class BabyMilestone_Base(BaseModel):
    b_id : int
    m_id : int
    d_id : int
    m_achieved : bool
    m_achieved_date : datetime
   
    model_config = ConfigDict(from_attributes=True)


class BabyMilestone_Create(BabyMilestone_Base):
    pass


class BabyMilestone_Update(BaseModel):
    m_achieved : bool
    d_id : int
    m_achieved_date: Optional[datetime] = None

class BabyMilestone_Read(BabyMilestone_Base):
    bm_id : int
    