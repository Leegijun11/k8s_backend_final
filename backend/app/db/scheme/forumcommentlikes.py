from pydantic import BaseModel, ConfigDict


class ForumCommentLikes_Read(BaseModel):
    fc_l_id: int
    fc_id: int
    u_id: int

    model_config = ConfigDict(from_attributes=True)



class ForumCommentLikes_Count(BaseModel):
    count: int