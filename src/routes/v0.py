from uuid import UUID

from fastapi import APIRouter

from src.types import requests, domain
from src import api
from src.sqlalchemy.connection import engine

router = APIRouter(
    prefix="/0",
    tags=["v0"]
)

### USER

@router.post("/users")
def post_user(user: requests.NewUser) -> domain.User:
    with engine.begin() as conn:
        s_user = api.create_user(conn, domain.User(**user.model_dump()))
    return s_user


@router.get("/users/{user_id}")
def get_user(user_id: UUID) -> domain.User:
    with engine.begin() as conn:
        user = api.get_user(conn, id=user_id)
    return user

@router.delete("/users/{user_id}")
def delete_user(user_id: UUID):
    with engine.begin() as conn:
        api.delete_user(conn, user_id)


### FOLLOW

@router.post("/follows")
def post_follow(follow: requests.NewFollow) -> domain.Follow:
    with engine.begin() as conn:
        s_follow = api.create_follow(conn, domain.Follow(**follow.model_dump()))
    return s_follow


@router.delete("/follows/{follower_id}/leaders/{leader_id}")
def delete_follow(follower_id: UUID, leader_id: UUID):
    with engine.begin() as conn:
        api.delete_follow(conn, domain.Follow(follower_id=follower_id, leader_id=leader_id))


### GOAL

@router.post("/goals")
def post_goal(goal: requests.NewGoal) -> domain.Goal:
    with engine.begin() as conn:
        s_goal = api.create_goal(conn, domain.Goal(**goal.model_dump()))
    return s_goal


@router.get("/goals")
def get_goals(user_id: UUID) -> list[domain.Goal]:
    with engine.begin() as conn:
        goals = api.get_goals(conn, user_id)
    return goals


@router.delete("/goals/{goal_id}")
def delete_goal(goal_id: UUID):
    with engine.begin() as conn:
        api.delete_goal(conn, goal_id)


### TASK

@router.post("/tasks")
def post_task(task: requests.NewTask) -> domain.Task:
    with engine.begin() as conn:
        s_task = api.create_task(conn, domain.Task(**task.model_dump()))
    return s_task


@router.get("/tasks")
def get_tasks(user_id: UUID | None = None, goal_id: UUID | None = None) -> list[domain.Task]:
    with engine.begin() as conn:
        tasks = api.get_tasks(conn, user_id=user_id, goal_id=goal_id)
    return tasks


@router.delete("/tasks/{task_id}")
def delete_task(task_id: UUID):
    with engine.begin() as conn:
        api.delete_task(conn, UUID(task_id))


### TIMELINES

@router.get("/timelines/{follower_id}/leaders")
def get_timeline_of_leaders(follower_id: UUID) -> list[domain.Post]:
    with engine.begin() as conn:
        timeline = api.generate_timeline_of_leaders(conn, follower_id)
    return timeline
