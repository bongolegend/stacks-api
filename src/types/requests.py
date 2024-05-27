from pydantic import BaseModel, EmailStr, field_validator, Field
from ulid import ULID


class NewUserRequest(BaseModel):
    email: EmailStr
    username: str = Field(..., min_length=3, max_length=15)

class NewGoalRequest(BaseModel):
    user_id: ULID
    description: str = Field(..., min_length=1, max_length=280)

    @field_validator('user_id', mode="before")
    @classmethod
    def validate_id(cls, value: str) -> ULID:
        return ULID.from_str(value)

class NewTaskRequest(BaseModel):
    user_id: ULID
    goal_id: ULID | None
    description: str = Field(..., min_length=1, max_length=280)

    @field_validator('user_id', mode="before")
    @classmethod
    def validate_id(cls, value: str) -> ULID:
        return ULID.from_str(value)

    @field_validator('goal_id', mode="before")
    @classmethod
    def validate_id(cls, value: str | None) -> ULID | None:
        if value is None:
            return None
        return ULID.from_str(value)

class NewFollowRequest(BaseModel):
    user_id: ULID
    leader_id: ULID

    @field_validator('user_id', "leader_id", mode="before")
    @classmethod
    def validate_id(cls, value: str) -> ULID:
        return ULID.from_str(value)
