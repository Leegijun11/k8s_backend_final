from pydantic import BaseModel, ConfigDict
from datetime import datetime
from typing import Optional

class ForumTag_Base(BaseModel):
    ft_sleep: bool=False
    ft_food: bool=False
    ft_health: bool=False
    ft_play: bool=False

    model_config = ConfigDict(from_attributes=True)


class ForumTag_Create(ForumTag_Base):
    pass


class ForumTag_Update(BaseModel):
    ft_sleep: Optional[bool] = None
    ft_food: Optional[bool] = None
    ft_health: Optional[bool] = None
    ft_play: Optional[bool] = None



class ForumTag_Read(ForumTag_Base):
    ft_id: int