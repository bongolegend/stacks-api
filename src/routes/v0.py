import logging
from uuid import UUID

from fastapi.responses import JSONResponse
from fastapi import APIRouter
from pydantic import EmailStr

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
    logging.debug(f"Creating user: {user}")
    with engine.begin() as conn:
        s_user = api.create_user(conn, domain.User(**user.model_dump()))
    return s_user


@router.get("/users/{user_id}")
def get_user(user_id: UUID) -> domain.User:
    with engine.begin() as conn:
        user = api.read_user(conn, id=user_id)
    return user

@router.get("/users")
def get_user(email: EmailStr | None = None, username: str | None = None) -> list[domain.User]:
    with engine.begin() as conn:
        assert len(username) >= 3
        user = api.read_user(conn, email=email, username=username)
    if user is None:
        return JSONResponse({"error": "User not found"}, status_code=404)
    return [user]

@router.get("/users/{user_id}/search")
def get_user_search(user_id: UUID) -> list[domain.UserEnriched]:
    with engine.begin() as conn:
        users = api.search_users(conn, user_id)
    logging.debug(f"Users: {users}")
    return users

@router.delete("/users/{user_id}")
def delete_user(user_id: UUID):
    with engine.begin() as conn:
        api.delete_user(conn, user_id)


@router.get("/users/leaders/{user_id}")
def get_leaders(user_id: UUID) -> list[domain.UserEnriched]:
    logging.debug(f"Getting leaders for user: {user_id}")
    with engine.begin() as conn:
        leaders = api.read_leaders(conn, user_id)
    logging.debug(f"Leaders: {leaders}")
    return leaders


@router.get("/users/followers/{user_id}")
def get_followers(user_id: UUID) -> list[domain.UserEnriched]:
    logging.debug(f"Getting followers for user: {user_id}")
    with engine.begin() as conn:
        followers = api.read_followers(conn, user_id)
    logging.debug(f"Followers: {followers}")
    return followers

### FOLLOW

@router.post("/follows")
def post_follow(follow: requests.NewFollow) -> domain.Follow:
    logging.debug(f"Creating follow: {follow}")
    with engine.begin() as conn:
        s_follow = api.create_follow(conn, domain.Follow(**follow.model_dump()))
    return s_follow


@router.delete("/follows/{follower_id}/leaders/{leader_id}")
def delete_follow(follower_id: UUID, leader_id: UUID):
    logging.debug(f"Deleting follow: {follower_id}")
    with engine.begin() as conn:
        api.delete_follow(conn, domain.Follow(follower_id=follower_id, leader_id=leader_id))

@router.get("/follows/counts/{user_id}")
def get_follow_counts(user_id: UUID) -> domain.FollowCounts:
    logging.debug(f"Getting follow counts for user: {user_id}")
    with engine.begin() as conn:
        counts = api.read_follow_counts(conn, user_id)
    logging.debug(f"Follow counts: {counts}")
    return counts

### GOAL

@router.post("/goals")
def post_goal(goal: requests.NewGoal) -> domain.Goal:
    logging.debug(f"Creating goal: {goal}")
    with engine.begin() as conn:
        s_goal = api.create_goal(conn, domain.Goal(**goal.model_dump()))
    return s_goal


@router.get("/goals")
def get_goals(user_id: UUID) -> list[domain.Goal]:
    logging.debug(f"Getting goals for user: {user_id}")
    with engine.begin() as conn:
        goals = api.read_goals(conn, user_id)
    logging.debug(f"Goals: {goals}")
    return goals


@router.patch("/goals/{goal_id}")
def patch_goal(goal_id: UUID, updates: requests.UpdateGoal) -> domain.Goal:
    logging.debug(f"Updating goal: {goal_id} with {updates}")
    with engine.begin() as conn:
        goal = api.update_goal(conn, goal_id, updates)
    return goal


@router.delete("/goals/{goal_id}")
def delete_goal(goal_id: UUID):
    with engine.begin() as conn:
        api.delete_goal(conn, goal_id)


### TASK

@router.post("/tasks")
def post_task(task: requests.NewTask) -> domain.Task:
    logging.debug(f"Creating task: {task}")
    with engine.begin() as conn:
        s_task = api.create_task(conn, domain.Task(**task.model_dump()))
    return s_task


@router.get("/tasks")
def get_tasks(user_id: UUID | None = None, goal_id: UUID | None = None) -> list[domain.Task]:
    logging.debug(f"Getting tasks for user: {user_id} and goal: {goal_id}")
    with engine.begin() as conn:
        tasks = api.read_tasks(conn, user_id=user_id, goal_id=goal_id)
    logging.debug(f"Tasks: {tasks}")
    return tasks

@router.patch("/tasks/{task_id}")
def patch_task(task_id: UUID, updates: requests.UpdateTask) -> domain.Task:
    logging.debug(f"Updating task: {task_id} with {updates}")
    with engine.begin() as conn:
        goal = api.update_task(conn, task_id, updates)
    logging.debug(f"Updated task: {goal}")
    return goal

@router.delete("/tasks/{task_id}")
def delete_task(task_id: UUID):
    with engine.begin() as conn:
        api.delete_task(conn, UUID(task_id))


### TIMELINES

@router.get("/timelines/{follower_id}/leaders")
def get_timeline_of_leaders(follower_id: UUID) -> list[domain.Post]:
    logging.debug(f"Getting timeline of leaders for user: {follower_id}")
    with engine.begin() as conn:
        timeline = api.generate_timeline_of_leaders(conn, follower_id)
    logging.debug(f"Timeline: {timeline}")
    return timeline


### REACTIONS

@router.post("/reactions")
def post_reaction(reaction: requests.NewReaction) -> domain.Reaction:
    logging.debug(f"Creating reaction: {reaction}")
    with engine.begin() as conn:
        s_reaction = api.create_reaction(conn, domain.Reaction(**reaction.model_dump()))
    return s_reaction


### COMMENTS

@router.post("/comments")
def post_comment(comment: requests.NewComment) -> domain.Comment:
    logging.debug(f"Creating comment: {comment}")
    with engine.begin() as conn:
        s_comment = api.create_comment(conn, domain.Comment(**comment.model_dump()))
    return s_comment

@router.get("/comments")
def get_comments(user_id: UUID | None = None, goal_id: UUID | None = None, task_id: UUID | None = None) -> list[domain.CommentEnriched]:    
    logging.debug(f"Getting comments for user: {user_id}, goal: {goal_id}, or task: {task_id}")
    with engine.begin() as conn:
        comments = api.read_comments(conn, user_id=user_id, goal_id=goal_id, task_id=task_id)
    logging.debug(f"Comments: {comments}")
    return comments