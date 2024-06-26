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

@router.get("/users/search/{user_id}")
def get_search_users(user_id: UUID) -> list[domain.UserEnriched]:
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
def get_goals(user_id: UUID) -> list[domain.GoalEnriched]:
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


### ANNOUNCEMENTS

@router.get("/announcements/{follower_id}")
def get_announcements(follower_id: UUID) -> list[domain.Announcement]:
    logging.debug(f"Getting announcements for user: {follower_id}")
    with engine.begin() as conn:
        timeline = api.generate_announcements(conn, follower_id)
    logging.debug(f"Announcements: {timeline}")
    return timeline


### REACTIONS

@router.post("/reactions")
def post_reaction(reaction: requests.NewReaction) -> domain.Reaction:
    logging.debug(f"Creating reaction: {reaction}")
    with engine.begin() as conn:
        s_reaction = api.create_reaction(conn, domain.Reaction(**reaction.model_dump()))
    return s_reaction

@router.get("/reactions")
def get_reactions(user_id: UUID | None = None, goal_id: UUID | None = None) -> list[domain.Reaction]:
    logging.debug(f"Getting reactions for user: {user_id}, goal: {goal_id}")
    with engine.begin() as conn:
        reactions = api.read_reactions(conn, user_id=user_id, goal_id=goal_id)
    logging.debug(f"Reactions: {reactions}")
    return reactions


### COMMENTS

@router.post("/comments")
def post_comment(comment: requests.NewComment) -> domain.Comment:
    logging.debug(f"Creating comment: {comment}")
    with engine.begin() as conn:
        s_comment = api.create_comment(conn, domain.Comment(**comment.model_dump()))
    return s_comment

@router.get("/comments")
def get_comments(user_id: UUID | None = None, goal_id: UUID | None = None) -> list[domain.CommentEnriched]:    
    logging.debug(f"Getting comments for user: {user_id}, goal: {goal_id}")
    with engine.begin() as conn:
        comments = api.read_comments(conn, user_id=user_id, goal_id=goal_id)
    logging.debug(f"Comments: {comments}")
    return comments
