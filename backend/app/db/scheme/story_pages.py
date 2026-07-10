from pydantic import BaseModel, ConfigDict
from datetime import date
from typing import Optional


class Story_Page_Base(BaseModel): 
    sp_content: str
    sp_image: str
    s_id: int

    model_config = ConfigDict(from_attributes=True)


class Story_Page_Create(Story_Page_Base):
    pass


class Story_Page_Read(Story_Page_Base):
    sp_id: int
    s_id: int