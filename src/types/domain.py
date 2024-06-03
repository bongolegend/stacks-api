# The types.domain should be used for all interfaces internal to the stacks-api service
from datetime import datetime, timezone
from typing_extensions import Self

from pydantic import BaseModel, Field, field_validator
from ulid import ULID
from uuid import UUID

from src.types import requests


class CustomBase(BaseModel):
    id: UUID = Field(default_factory=lambda: ULID().to_uuid4())
    created_at: datetime | None = None
    updated_at: datetime | None = None

    @field_validator("id", mode="before")
    @classmethod
    def validate_id(cls, value):
        return requests.validate_uuid(value)

class User(CustomBase, requests.NewUser):
    pass

class UserEnriched(User):
    leader: bool = False

class Goal(CustomBase, requests.NewGoal):
    pass

class Task(CustomBase, requests.NewTask):
    pass

class Follow(requests.NewFollow):
    created_at: datetime | None = None
    updated_at: datetime | None = None

class Post(BaseModel):
    """A Post is an entity in a timeline. It is a way to share goals and tasks"""
    id: UUID = Field(default_factory=lambda: ULID().to_uuid4())
    user: User
    primary: Goal | Task
    secondary: Goal | None = None
    sort_on: datetime
    created_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
