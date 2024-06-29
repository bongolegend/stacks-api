from datetime import datetime
from uuid import UUID
from pydantic import BaseModel, EmailStr, field_validator, Field, model_validator


def validate_uuid(value) -> UUID:
    if isinstance(value, str):
        return UUID(value)
    if isinstance(value, UUID):
        return value

class NewUser(BaseModel):
    email: EmailStr
    username: str = Field(..., min_length=3, max_length=15)

class NewGoal(BaseModel):
    user_id: UUID
    description: str = Field(..., min_length=1, max_length=1000)
    parent_id: UUID | None = None
    title: str | None = Field(default=None, min_length=1, max_length=100)
    due_date: datetime | None = None
    is_completed: bool = False

    @field_validator('user_id', 'parent_id', mode="before")
    @classmethod
    def validate_id(cls, value):
        return validate_uuid(value)

class UpdateGoal(BaseModel):
    title: str | None = Field(None, min_length=1, max_length=100)
    description: str | None = Field(None, min_length=1, max_length=1000)
    due_date: datetime | None = None
    is_completed: bool | None = None

class NewFollow(BaseModel):
    follower_id: UUID
    leader_id: UUID

    @field_validator('follower_id', "leader_id", mode="before")
    @classmethod
    def validate_id(cls, value):
        return validate_uuid(value)

class NewReaction(BaseModel):
    user_id: UUID
    goal_id: UUID
    reaction: dict
    reaction_library: str

    @field_validator('user_id', 'goal_id', mode="before")
    @classmethod
    def validate_id(cls, value):
        return validate_uuid(value)


class NewComment(BaseModel):
    user_id: UUID
    goal_id: UUID
    comment: str

    @field_validator('user_id', 'goal_id', mode="before")
    @classmethod
    def validate_id(cls, value):
        return validate_uuid(value)


class UpdateUnreadComments(BaseModel):
    user_id: UUID
    comment_ids: list[UUID]

    @field_validator('user_id', 'comment_ids', mode="before")
    @classmethod
    def validate_id(cls, value):
        if isinstance(value, list):
            return [validate_uuid(v) for v in value]
        return validate_uuid(value)