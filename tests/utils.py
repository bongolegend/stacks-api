from sqlalchemy import MetaData, delete, insert
from sqlalchemy.engine import Connection
from ulid import ULID

from src.types import requests, domain
from src.postgres.connection import engine
from src.postgres import tables

DONT_DELETE_FROM_THESE = ("alembic_version",)

def delete_all_entries_from_db():
    metadata = MetaData()
    metadata.reflect(bind=engine)
    with engine.begin() as conn:
        for table in reversed(metadata.sorted_tables):
            if table.name not in DONT_DELETE_FROM_THESE:
                conn.execute(delete(table))

def create_users_for_tests(conn: Connection, count = 2) -> list[domain.User]:
    """Create users and commit them to db."""
    users = []
    for i in range(count):
        users.append(domain.User(email=f"u{i}@a.b", username=f"user{i}").model_dump(exclude_none=True))
    inserted = conn.execute(insert(tables.users).values(users).returning(tables.users)).all()
    conn.commit()
    inserted = [domain.User(**row._mapping) for row in inserted]
    return inserted

def create_goals_for_tests(conn: Connection, users: list[domain.User], count = 2) -> list[domain.Goal]:
    """Create `count` goals for each user and commit them to db."""
    goals = []
    for u in users:
        for i in range(count):
            goals.append(domain.Goal(user_id=u.id, description="goal-description").model_dump(exclude_none=True))
    inserted = conn.execute(insert(tables.goals).values(goals).returning(tables.goals)).all()
    conn.commit()
    inserted = [domain.Goal(**row._mapping) for row in inserted]
    return inserted

def create_tasks_for_tests(conn: Connection, goals: list[domain.Goal], count = 2) -> list[domain.Task]:
    tasks = [
        domain.Task(user_id=g.user_id, goal_id=g.id, description="task-desc").model_dump(exclude_none=True) 
        for _ in range(count) 
        for g in goals]
    inserted = conn.execute(insert(tables.tasks).values(tasks).returning(tables.tasks)).all()
    conn.commit()
    inserted = [domain.Task(**row._mapping) for row in inserted]
    return inserted
