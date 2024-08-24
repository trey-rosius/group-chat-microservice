from datetime import datetime
from enum import Enum
from typing import Optional

from pydantic import BaseModel, EmailStr


class UserModel(BaseModel):
    id: str
    email: EmailStr
    username: str
    profile_pic_url: Optional[str]
    created_at: int
    updated_at: Optional[int]
