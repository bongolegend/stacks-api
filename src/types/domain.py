# The types.domain should be used for all interfaces internal to the stacks-api service
from datetime import datetime, timezone
from typing_extensions import Self

from pydantic import BaseModel, Field, model_validator
from ulid import ULID
from uuid import UUID

from src.types import requests


class CustomBase(BaseModel):
    id: UUID = Field(default_factory=lambda: ULID().to_uuid4())
    created_at: datetime | None = None
    updated_at: datetime | None = None

class User(CustomBase, requests.NewUser):
    pass

class Goal(CustomBase, requests.NewGoal):
    pass

class Task(CustomBase, requests.NewTask):
    pass

class Follow(requests.NewFollow):
    created_at: datetime | None = None
    updated_at: datetime | None = None

class Brick(BaseModel):
    """A Brick is an entity in a feed. It can be a goal or a task"""
    user: User
    primary: Goal | Task
    secondary: Goal | None = None
    created_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))

    @model_validator(mode="after")
    def check_fields(self) -> Self:
        if isinstance(self.primary, Goal) and self.secondary is not None:
            raise ValueError('secondary must be None if primary is `domain.Goal`')
        if isinstance(self.primary, Task) and self.secondary is None:
            raise ValueError('secondary must be `domain.Goal` if primary is `domain.Task`')
        return self
