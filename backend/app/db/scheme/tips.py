from pydantic import BaseModel, Field, ConfigDict


class Tip_Base(BaseModel): 
    t_title: str
    t_age: int
    t_content: str

    model_config = ConfigDict(from_attributes=True)

    
class Tip_Read(Tip_Base):
    t_id: int
    