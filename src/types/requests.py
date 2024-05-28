from uuid import UUID, uuid4
from ulid import ULID
from pydantic import BaseModel, EmailStr, field_validator, Field


def _validate_id(value) -> UUID:
    if isinstance(value, str):
        return UUID(value)
    if isinstance(value, UUID):
        return value

class CustomBase(BaseModel):
    id: UUID = Field(default_factory=lambda: ULID().to_uuid4())

class NewUser(CustomBase):
    email: EmailStr
    username: str = Field(..., min_length=3, max_length=15)

class NewGoal(CustomBase):
    user_id: UUID
    description: str = Field(..., min_length=1, max_length=280)

    @field_validator('user_id', mode="before")
    @classmethod
    def validate_id(cls, value):
        return _validate_id(value)

class NewTask(CustomBase):
    user_id: UUID
    goal_id: UUID
    description: str = Field(..., min_length=1, max_length=280)

    @field_validator('user_id', 'goal_id', mode="before")
    @classmethod
    def validate_id(cls, value):
        return _validate_id(value)

class Follow(BaseModel):
    follower_id: UUID
    leader_id: UUID

    @field_validator('follower_id', "leader_id", mode="before")
    @classmethod
    def validate_id(cls, value):
        return _validate_id(value)
