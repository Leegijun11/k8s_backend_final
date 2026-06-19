from pydantic import BaseModel, Field, ConfigDict


class Parent_Base(BaseModel): 
    p_role: str
    p_category : str
    p_state: str

    model_config = ConfigDict(from_attributes=True)


class Parent_Create(Parent_Base):
    g_id : int
    u_id : int
    

class Parent_Update(Parent_Base):
    current_b_id : int | None=None

    
class Parent_Read(Parent_Create):
    current_b_id : int

