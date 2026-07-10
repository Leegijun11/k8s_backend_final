from pydantic import BaseModel, ConfigDict
from datetime import datetime

class ForumLike_Read(BaseModel):
    f_l_id: int
    f_id: int
    u_id: int

    model_config = ConfigDict(from_attributes=True)


# GET /forumlike/count/{f_id} 응답용 스키마
class ForumLikeCount_Response(BaseModel):
    count: int