from typing import Optional
from pydantic import BaseModel


class GroupModel(BaseModel):
    id: str
    group_name: str
    group_description: str
    created_by: str
    group_url: str
    created_at: int
    updated_at: Optional[int]
