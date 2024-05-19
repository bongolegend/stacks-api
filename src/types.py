from pydantic import BaseModel, EmailStr
from datetime import datetime
from typing import Optional


class CommonBaseModel(BaseModel):
    id: Optional[int]
    created_at: Optional[datetime]
    updated_at: Optional[datetime]

    class Config:
        from_attributes = True

class User(CommonBaseModel):
    username: str
    email: EmailStr

class Task(CommonBaseModel):
    title: str
    description: Optional[str] = None
    due_date: datetime
    is_completed: bool = False
    user_id: int
    goal_id: Optional[int] = None

class Goal(CommonBaseModel):
    title: str
    description: Optional[str] = None
    due_date: datetime
    is_completed: bool = False
    user_id: int
