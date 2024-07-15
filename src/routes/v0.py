from typing import Annotated
import structlog
from uuid import UUID
import os
import time 

from fastapi.responses import JSONResponse
from fastapi import APIRouter, Query, Header
from pydantic import EmailStr
from jose import JWTError

from src.types import requests, domain
from src import api
from src.sqlalchemy.connection import engine
from src.auth import create_access_token, verify_firebase_token, verify_token

log = structlog.get_logger()

router = APIRouter(
    prefix="/0",
    tags=["v0"]
)

ENV = os.getenv("ENV")

### USER

@router.get("/users/login")
def get_user_login(email: EmailStr, authorization: str = Header(...)) -> domain.UserAuth:
    log.debug("Logging in user", email=email)
    if ENV == "test":
        log.info("logging in without firebase authentication", email=email)
        with engine.begin() as conn:
            user = api.read_user(conn, email=email)
    else:
        firebase_id = verify_firebase_token(authorization)
        with engine.begin() as conn:
            user = api.read_user(conn, firebase_id=firebase_id)
    if user is None:
        return JSONResponse({"error": "User not found"}, status_code=404)
    access_token = create_access_token(user.id)
    return domain.UserAuth(**user.model_dump(), access_token=access_token)


@router.post("/users")
def post_user(user: requests.NewUser, authorization: str= Header(...)) -> domain.UserAuth:
    log.debug("Creating user", user=user)
    # TODO: add test env to config. This exists so unit tests don't use firebase 
    if ENV == "test":
        log.info("create user without firebase authentication", email=user.email)
        firebase_id = None
    else:
        firebase_id = verify_firebase_token(authorization)
    with engine.begin() as conn:
        new_user = api.create_user(conn, domain.UserFirebase(**user.model_dump(),firebase_id = firebase_id))
    access_token = create_access_token(new_user.id)
    return domain.UserAuth(**new_user.model_dump(), access_token=access_token)


@router.get("/users/{user_id}")
def get_user(user_id: UUID, authorization: str= Header(...)) -> domain.User:
    try: 
        # TODO: could use userid from auth instead of user_id
        verify_token(authorization)
        with engine.begin() as conn:
            user = api.read_user(conn, id=user_id)
        return user
    except JWTError as e:
        log.error("Invalid Access Token", error_message=str(e))

# TODO: Figure out if endpoint below is being used - I think not...
@router.get("/users")
def get_user(
    email: EmailStr | None = None, 
    username: str | None = None, 
    authorization: str= Header(...)
    ) -> list[domain.User]:
    try: 
        verify_token(authorization)
        with engine.begin() as conn:
            assert len(username) >= 3
            user = api.read_user(conn, email=email, username=username)
        if user is None:
            return JSONResponse({"error": "User not found"}, status_code=404)
        return [user]
    except JWTError as e:
        log.error("Invalid Access Token", error_message=str(e))


@router.get("/users/search/{user_id}")
def get_search_users(user_id: UUID, authorization: str= Header(...)) -> list[domain.UserEnriched]:
    try:
        verify_token(authorization)
        with engine.begin() as conn:
            users = api.search_users(conn, user_id)
        log.debug("Users", users=users)
        return users
    except JWTError as e:
        log.error("Invalid Access Token", error_message=str(e))


@router.delete("/users/{user_id}")
def delete_user(user_id: UUID, authorization: str= Header(...)):
    try:
        verify_token(authorization)
        with engine.begin() as conn:
            api.delete_user(conn, user_id)
    except JWTError as e:
        log.error("Invalid Access Token", error_message=str(e))


@router.get("/users/leaders/{user_id}")
def get_leaders(user_id: UUID, authorization: str= Header(...)) -> list[domain.UserEnriched]:
    log.debug("Getting leaders for user", user_id=user_id)
    try:
        verify_token(authorization)
        with engine.begin() as conn:
            leaders = api.read_leaders(conn, user_id)
        log.debug("Leaders", leaders=leaders)
        return leaders
    except JWTError as e:
        log.error("Invalid Access Token", error_message=str(e))


@router.get("/users/followers/{user_id}")
def get_followers(user_id: UUID, authorization: str= Header(...)) -> list[domain.UserEnriched]:
    log.debug("Getting followers for user", user_id=user_id)
    try:
        verify_token(authorization)
        with engine.begin() as conn:
            followers = api.read_followers(conn, user_id)
        log.debug("Followers", followers=followers)
        return followers
    except JWTError as e:
        log.error("Invalid Access Token", error_message=str(e))

### FOLLOW

@router.post("/follows")
def post_follow(follow: requests.NewFollow, authorization: str= Header(...)) -> domain.Follow:
    log.debug("Creating follow", follow=follow)
    try:
        verify_token(authorization)
        with engine.begin() as conn:
            s_follow = api.create_follow(conn, domain.Follow(**follow.model_dump()))
        return s_follow
    except JWTError as e:
        log.error("Invalid Access Token", error_message=str(e))


@router.delete("/follows/{follower_id}/leaders/{leader_id}")
def delete_follow(follower_id: UUID, leader_id: UUID, authorization: str= Header(...)):
    log.debug("Deleting follow", follower_id=follower_id, leader_id=leader_id)
    try:
        verify_token(authorization)
        with engine.begin() as conn:
            api.delete_follow(conn, domain.Follow(follower_id=follower_id, leader_id=leader_id))
    except JWTError as e:
        log.error("Invalid Access Token", error_message=str(e))

@router.get("/follows/counts/{user_id}")
def get_follow_counts(user_id: UUID, authorization: str= Header(...)) -> domain.FollowCounts:
    log.debug("Getting follow counts for user", user_id=user_id)
    try:
        verify_token(authorization)
        with engine.begin() as conn:
            counts = api.read_follow_counts(conn, user_id)
        log.debug("Follow counts", counts=counts)
        return counts
    except JWTError as e:
        log.error("Invalid Access Token", error_message=str(e))

### GOAL

@router.post("/goals")
def post_goal(goal: requests.NewGoal, authorization: str = Header(...)) -> domain.Goal:
    log.debug("Creating goal", goal=goal)
    try: 
        verify_token(authorization)        
        with engine.begin() as conn:
            s_goal = api.create_goal(conn, domain.Goal(**goal.model_dump()))
            api.create_comment_sub(conn, domain.CommentSub(goal_id=s_goal.id, user_id=s_goal.user_id))
        return s_goal
    except JWTError as e:
        log.error("Invalid Access Token", error_message=str(e))


@router.get("/goals")
def get_goals(
    user_id: UUID = None, 
    goal_ids: Annotated[list[UUID], Query()] = None,
    authorization: str= Header(...)
    ) -> list[domain.GoalEnriched]:
    log.debug("Getting goals", user_id=user_id, goal_ids=goal_ids)
    try:
        verify_token(authorization)
        with engine.begin() as conn:
            goals = api.read_goals(conn, user_id=user_id, goal_ids=goal_ids)
        # log.debug("Goals", goals=goals)
        return goals
    except JWTError as e:
        log.error("Invalid Access Token", error_message=str(e))


@router.get("/goals/announcements/{user_id}")
def get_announcements(user_id: UUID, authorization: str= Header(...)) -> list[domain.GoalEnriched]:
    log.debug("Getting announcements for user", user_id=user_id)
    try:
        verify_token(authorization)
        with engine.begin() as conn:
            announcements = api.read_announcements(conn, user_id)
        # log.debug("Announcements", announcements=announcements)
        return announcements
    except JWTError as e:
        log.error("Invalid Access Token", error_message=str(e))


@router.patch("/goals/{goal_id}")
def patch_goal(goal_id: UUID, updates: requests.UpdateGoal, authorization: str= Header(...)) -> domain.Goal:
    log.debug("Updating goal", goal_id=goal_id, updates=updates)
    try:
        verify_token(authorization)
        with engine.begin() as conn:
            goal = api.update_goal(conn, goal_id, updates)
        return goal
    except JWTError as e:
        log.error("Invalid Access Token", error_message=str(e))


@router.delete("/goals/{goal_id}")
def delete_goal(goal_id: UUID, authorization: str= Header(...)):
    try:
        verify_token(authorization)
        with engine.begin() as conn:
            api.delete_goal(conn, goal_id)
    except JWTError as e:
        log.error("Invalid Access Token", error_message=str(e))

### REACTIONS

@router.post("/reactions")
def post_reaction(reaction: requests.NewReaction, authorization: str= Header(...)) -> domain.Reaction:
    log.debug("Creating reaction", reaction=reaction)
    try:
        verify_token(authorization)
        with engine.begin() as conn:
            s_reaction = api.create_reaction(conn, domain.Reaction(**reaction.model_dump()))
        return s_reaction
    except JWTError as e:
        log.error("Invalid Access Token", error_message=str(e))


@router.get("/reactions")
def get_reactions(goal_ids: Annotated[list[UUID], Query()] = None, authorization: str= Header(...)) -> dict[UUID, list[domain.Reaction]]:
    log.debug("Getting reactions for goals", goal_ids=goal_ids)
    try:
        verify_token(authorization)
        with engine.begin() as conn:
            reactions = api.read_reactions(conn, goal_ids=goal_ids)
        # log.debug("Reactions", reactions=reactions)
        return reactions
    except JWTError as e:
        log.error("Invalid Access Token", error_message=str(e))

### COMMENTS

@router.post("/comments")
def post_comment(comment: requests.NewComment, authorization: str= Header(...)) -> domain.Comment:
    log.debug("Creating comment", comment=comment)
    try:
        verify_token(authorization)
        with engine.begin() as conn:
            s_comment = api.create_comment(conn, domain.Comment(**comment.model_dump()))
            api.create_unread_comments(conn, s_comment)
            # sub after creating the unreads because you don't want to notify the user of their own comment
            api.create_comment_sub(conn, domain.CommentSub(goal_id=s_comment.goal_id, user_id=s_comment.user_id))
        return s_comment
    except JWTError as e:
        log.error("Invalid Access Token", error_message=str(e))


@router.get("/comments")
def get_comments(
    user_id: UUID | None = None, 
    goal_id: UUID | None = None, 
    authorization: str= Header(...)
    ) -> list[domain.CommentEnriched]:    
    log.debug("Getting comments", user_id=user_id, goal_id=goal_id)
    try:
        verify_token(authorization)
        with engine.begin() as conn:
            comments = api.read_comments(conn, user_id=user_id, goal_id=goal_id)
        # log.debug("Comments", comments=comments)
        return comments
    except JWTError as e:
        log.error("Invalid Access Token", error_message=str(e))


@router.get("/comments/count")
def get_comment_counts(goal_ids: Annotated[list[UUID], Query()] = None, authorization: str= Header(...)) -> list[domain.CommentCount]:
    log.debug("Getting comment count for goals", goal_ids=goal_ids)
    try:
        verify_token(authorization)
        with engine.begin() as conn:
            counts = api.read_comment_counts(conn, goal_ids)
        return counts   
    except JWTError as e:
        log.error("Invalid Access Token", error_message=str(e))


@router.get("/comments/unread/count/{user_id}")
def get_unread_comments(user_id: UUID, authorization: str= Header(...)) -> int:
    log.debug("Getting unread comment count for user", user_id=user_id)
    try:
        verify_token(authorization)
        with engine.begin() as conn:
            count = api.read_unread_comment_count(conn, user_id)
        log.debug("Unread comment count", count=count)
        return count
    except JWTError as e:
        log.error("Invalid Access Token", error_message=str(e))


@router.patch("/comments/unread")
def patch_unread_comments(body: requests.UpdateUnreadComments, authorization: str= Header(...)) -> None:
    try:
        verify_token(authorization)
        user_id = body.user_id
        comment_ids = body.comment_ids
        log.debug("Updating unread comments", user_id=user_id, comment_ids=comment_ids)
        with engine.begin() as conn:
            api.update_unread_comments(conn, user_id, comment_ids)
    except JWTError as e:
        log.error("Invalid Access Token", error_message=str(e))


@router.get("/comments/unread")
def get_unread_comments(user_id: UUID, authorization: str= Header(...)) -> list[domain.CommentEnriched]:
    log.debug("Getting unread comments for user", user_id=user_id)
    try:
        verify_token(authorization)
        with engine.begin() as conn:
            comments = api.read_unread_comments(conn, user_id)
        log.debug("Unread comments", comments=comments)
        return comments
    except JWTError as e:
        log.error("Invalid Access Token", error_message=str(e))