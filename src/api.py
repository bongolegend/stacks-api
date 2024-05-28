from sqlalchemy.orm import Session
from ulid import ULID
from uuid import UUID

from src.postgres import models
from src.types import requests

### USER

def create_user(db: Session, user: requests.NewUser) -> models.User:
    db_user = models.User(id=ULID().to_uuid4(), username=user.username, email=user.email)
    db.add(db_user)
    db.commit()
    db.refresh(db_user)
    return db_user

def create_user_if_new(db: Session, user: requests.NewUser) -> models.User:
    existing_user = get_user_by_email(db, email=user.email)
    if existing_user:
        raise Exception(status_code=400, message="Email already registered")
    return create_user(db, user)

def get_user_by_email(db: Session, email: str) -> models.User:
    return db.query(models.User).filter(models.User.email == email).first()

def get_user_by_username():
    pass

def get_user_by_id():
    pass

def get_followers(db: Session, user_id: UUID) -> list[models.User]:
    pass

def get_leaders(db: Session, user_id: UUID) -> list[models.User]:
    pass

def delete_user(db: Session, user_id: UUID) -> None:
    db.query(models.User).filter(models.User.id == user_id).delete()
    db.commit()

### FOLLOW

def create_follow(db: Session, follow: requests.Follow) -> models.Follow:
    db_follow = models.Follow(**follow.model_dump())
    db.add(db_follow)
    db.commit()
    db.refresh(db_follow)
    return db_follow

def delete_follow(db: Session, follow: requests.Follow):
    db.query(models.Follow) \
        .filter(models.Follow.follower_id == follow.follower_id) \
        .filter(models.Follow.leader_id == follow.leader_id) \
        .delete()
    db.commit()

### GOAL

def create_goal(db: Session, goal: requests.NewGoal) -> models.Goal:
    db_goal = models.Goal(id=ULID().to_uuid4(), **goal.model_dump())
    db.add(db_goal)
    db.commit()
    db.refresh(db_goal)
    return db_goal

def get_goals(db: Session, user_ids: list[UUID]) -> list[models.Goal]:
    pass

def delete_goal(db: Session, goal_id: UUID):
    db.query(models.Goal).filter(models.Goal.id == goal_id).delete()
    db.commit()

### TASK

def create_task(db: Session, task: requests.NewTask) -> models.Task:
    db_task = models.Task(id=ULID().to_uuid4(), **task.model_dump())
    db.add(db_task)
    db.commit()
    db.refresh(db_task)
    return db_task

def delete_task(db: Session, task_id: UUID):
    db.query(models.Task).filter(models.Task.id == task_id).delete()
    db.commit()
