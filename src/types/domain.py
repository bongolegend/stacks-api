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
    leader: bool | None = None
    follower: bool | None = None

class Goal(CustomBase, requests.NewGoal):
    pass

class Follow(requests.NewFollow):
    created_at: datetime | None = None
    updated_at: datetime | None = None

class FollowCounts(BaseModel):
    followers: int = 0
    leaders: int = 0
class Reaction(CustomBase, requests.NewReaction):
    pass

class Comment(CustomBase, requests.NewComment):
    pass

class CommentEnriched(Comment):
    user: User


class GoalEnriched(Goal):
    user: User
    parent: Goal | None = None


class CommentCount(BaseModel):
    goal_id: UUID
    count: int = 0

class CommentSub(CustomBase):
    goal_id: UUID
    user_id: UUID

class UnreadComment(CustomBase):
    user_id: UUID
    goal_id: UUID
    comment_id: UUID
    read: bool = False
