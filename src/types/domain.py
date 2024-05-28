# The types.domain should be used for all interfaces internal to the stacks-api service
from datetime import datetime

from pydantic import BaseModel, Field
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

    
