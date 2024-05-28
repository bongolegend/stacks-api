from sqlalchemy import select, insert, delete, update, and_, or_, false
from ulid import ULID
from uuid import UUID

from src.postgres import tables
from src.types import requests, domain
from sqlalchemy.engine import Connection


### USER

def create_user(conn: Connection, user: domain.User) -> domain.User:
    stmt = insert(tables.users).values(**user.model_dump()).returning(tables.users)
    inserted = conn.execute(stmt).fetchone()._mapping
    return domain.User(**inserted)

def get_user(
        conn: Connection,
        id: UUID = None,
        username: str = None, 
        email: str = None) -> domain.User | None:
    if [id, username, email].count(None) != 2:
        raise ValueError("You must exactly one of id, username or email")
    if id:
        filter = tables.users.c.id == id
    if username:
        filter = tables.users.c.username == username
    if email:
        filter = tables.users.c.email == email
    stmt = select(tables.users).where(filter)
    result = conn.execute(stmt).fetchone()
    if result is None:
        return
    return domain.User(**result._mapping)

def get_followers(conn: Connection, leader_id: UUID) -> list[domain.User]:
    stmt = select(tables.users) \
        .select_from(tables.users) \
        .join(tables.follows, tables.users.c.id == tables.follows.c.follower_id) \
        .where(tables.follows.c.leader_id == leader_id)
    result = conn.execute(stmt).all()
    followers = [domain.User(**row._mapping) for row in result]
    return followers

def get_leaders(conn: Connection, follower_id: UUID) -> list[domain.User]:
    stmt = select(tables.users) \
        .select_from(tables.users) \
        .join(tables.follows, tables.users.c.id == tables.follows.c.leader_id) \
        .where(tables.follows.c.follower_id == follower_id)
    result = conn.execute(stmt).all()
    leaders = [domain.User(**row._mapping) for row in result]
    return leaders

def delete_user(conn: Connection, user_id: UUID) -> None:
    stmt = delete(tables.users).where(tables.users.c.id == user_id)
    conn.execute(stmt)

### FOLLOW

def create_follow(conn: Connection, follow: domain.Follow) -> domain.Follow:
    stmt = insert(tables.follows) \
        .values(follower_id=follow.follower_id, leader_id=follow.leader_id) \
        .returning(tables.follows)
    follow = conn.execute(stmt).fetchone()
    return domain.Follow(**follow._mapping)

def delete_follow(conn: Connection, follow: domain.Follow) -> None:
    stmt = delete(tables.follows).where(
        and_(tables.follows.c.follower_id == follow.follower_id,
             tables.follows.c.leader_id == follow.leader_id))
    conn.execute(stmt)

### GOAL

def create_goal(conn: Connection, goal: domain.Goal) -> domain.Goal:
    stmt = insert(tables.goals).values(**goal.model_dump()).returning(tables.goals)
    inserted = conn.execute(stmt).fetchone()
    return domain.Goal(**inserted._mapping)

def get_goals(conn: Connection, user_id: UUID) -> list[domain.Goal]:
    stmt = select(tables.goals).where(tables.goals.c.user_id == user_id)
    result = conn.execute(stmt).all()
    goals = [domain.Goal(**row._mapping) for row in result]
    return goals

def delete_goal(conn: Connection, goal_id: UUID) -> None:
    stmt = delete(tables.goals).where(tables.goals.c.id == goal_id)
    conn.execute(stmt)

### TASK

def create_task(conn: Connection, task: domain.Task) -> domain.Task:
    stmt = insert(tables.tasks).values(**task.model_dump()).returning(tables.tasks)
    inserted = conn.execute(stmt).fetchone()
    return domain.Task(**inserted._mapping)

def get_tasks(conn: Connection, user_id: UUID = None, goal_id: UUID = None) -> list[domain.Task]:
    if [user_id, goal_id].count(None) != 1:
        raise Exception("You must specify exactly one of `user_id`, `goal_id`")
    if user_id:
        filter = tables.tasks.c.user_id == user_id
    elif goal_id:
        filter = tables.tasks.c.goal_id == goal_id
    stmt = select(tables.tasks).where(filter)
    result = conn.execute(stmt).all()
    if not result:
        return []
    tasks = [domain.Task(**row._mapping) for row in result]
    return tasks

def delete_task(conn: Connection, task_id: UUID) -> None:
    stmt = delete(tables.tasks).where(tables.tasks.c.id == task_id)
    conn.execute(stmt)
