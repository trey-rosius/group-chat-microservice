from enum import Enum
from typing import Optional
from pydantic import BaseModel


class TypingModel(BaseModel):
    id: str
    userId: str
    groupId: str
    typing: bool
