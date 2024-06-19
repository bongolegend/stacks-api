# The types.requests should only be used to validate requests in FastAPI
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
    description: str = Field(..., min_length=1, max_length=280)
    is_completed: bool = False

    @field_validator('user_id', mode="before")
    @classmethod
    def validate_id(cls, value):
        return validate_uuid(value)

class UpdateGoal(BaseModel):
    description: str | None = Field(None, min_length=1, max_length=280)
    is_completed: bool | None = None

class NewTask(BaseModel):
    user_id: UUID
    goal_id: UUID
    description: str = Field(..., min_length=1, max_length=280)
    is_completed: bool = False

    @field_validator('user_id', 'goal_id', mode="before")
    @classmethod
    def validate_id(cls, value):
        return validate_uuid(value)

class UpdateTask(BaseModel):
    description: str | None = Field(None, min_length=1, max_length=280)
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
    reaction: dict
    reaction_library: str
    task_id: UUID | None = None
    goal_id: UUID | None = None

    @field_validator('user_id', 'task_id', 'goal_id', mode="before")
    @classmethod
    def validate_id(cls, value):
        return validate_uuid(value)
    
    @model_validator(mode="before")
    @classmethod
    def check_task_or_goal_id(cls, values):
        task_id = values.get('task_id')
        goal_id = values.get('goal_id')

        if (task_id is None and goal_id is None) or (task_id is not None and goal_id is not None):
            raise ValueError('Exactly one of task_id or goal_id must be provided')

        return values