from pydantic import BaseModel, ConfigDict


class CareGroup_Base(BaseModel): 
    creator_id: int

    model_config = ConfigDict(from_attributes=True)


class CareGroup_Create(CareGroup_Base):
    pass
    

class CareGroup_Read(CareGroup_Base):
    g_id: int

