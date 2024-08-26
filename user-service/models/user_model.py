from datetime import datetime
from enum import Enum
from typing import Optional

from pydantic import BaseModel


class UserModel(BaseModel):
    id: str
    email: str
    username: str
    profile_pic_url: Optional[str]
    created_at: int
    updated_at: Optional[int]
