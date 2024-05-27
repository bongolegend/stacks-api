from sqlalchemy.orm import Session
from ulid import ULID
from uuid import UUID

from src.postgres import models
from src.types import requests


def get_user_by_email(db: Session, email: str) -> models.User:
    return db.query(models.User).filter(models.User.email == email).first()

def create_user(db: Session, user: requests.NewUser) -> models.User:
    db_user = models.User(id=ULID().to_uuid4(), username=user.username, email=user.email)
    db.add(db_user)
    db.commit()
    db.refresh(db_user)
    return db_user

def delete_user(db: Session, user_id: UUID) -> None:
    db.query(models.User).filter(models.User.id == user_id).delete()
    db.commit()

def create_user_if_new(db: Session, user: requests.NewUser) -> models.User:
    existing_user = get_user_by_email(db, email=user.email)
    if existing_user:
        raise Exception(status_code=400, message="Email already registered")
    return create_user(db, user)

def create_follow(db: Session, follow: requests.Follow):
    follower = db.query(models.User).filter(models.User.id == follow.follower_id).first()
    leader = db.query(models.User).filter(models.User.id == follow.leader_id).first()
    follower.is_following.append(leader)
    db.commit()

def delete_follow(db: Session, follow: requests.Follow):
    follower = db.query(models.User).filter(models.User.id == follow.follower_id).first()
    leader = db.query(models.User).filter(models.User.id == follow.leader_id).first()
    follower.is_following.remove(leader)
    db.commit()

    