from datetime import datetime
from pytz import utc

from sqlalchemy import MetaData, delete, insert
from sqlalchemy.engine import Connection

from src.types import domain
from src.sqlalchemy.connection import engine
from src.sqlalchemy import tables

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
            goals.append(domain.Goal(
                user_id=u.id, title="title", description="goal-description", due_date=datetime.now(utc)).model_dump(exclude_none=True))
    inserted = conn.execute(insert(tables.goals).values(goals).returning(tables.goals)).all()
    conn.commit()
    inserted = [domain.Goal(**row._mapping) for row in inserted]
    return inserted


def create_milestones_for_tests(conn: Connection, goals: list[domain.Goal], count = 2) -> list[domain.Goal]:
    subgoals = []
    for g in goals:
        for i in range(count):
            subgoals.append(domain.Goal(
                user_id=g.user_id, parent_id=g.id, description="subgoal-description").model_dump(exclude_none=True))
    inserted = conn.execute(insert(tables.goals).values(subgoals).returning(tables.goals)).all()
    conn.commit()
    inserted = [domain.Goal(**row._mapping) for row in inserted]
    return inserted


def create_reactions_for_tests(
        conn: Connection, user: domain.User, 
        goals: list[domain.Goal], 
        count = 2) -> list[domain.Reaction]:
    reactions = []

    for g in goals:
        for i in range(count):
            reactions.append(domain.Reaction(**{"goal_id": g.id}, user_id=user.id, reaction={
                'name': 'beaming face with smiling eyes', 
                'emoji': '😁', 
                'unicode_version': '0.6', 
                'slug': 'beaming_face_with_smiling_eyes', 
                'toneEnabled': False},
                reaction_library='rn-emoji-keyboard:^1.7.0').model_dump(exclude_none=True))
    inserted = conn.execute(insert(tables.reactions).values(reactions).returning(tables.reactions)).all()
    conn.commit()
    inserted = [domain.Reaction(**row._mapping) for row in inserted]
    return inserted

def create_comments_for_tests(
        conn: Connection, user: domain.User, 
        goals: list[domain.Goal], 
        count = 2) -> list[domain.Comment]:
    comments = []
    for g in goals:
        for i in range(count):
            comments.append(domain.Comment(**{"goal_id": g.id}, user_id=user.id, comment="comment").model_dump(exclude_none=True))
    inserted = conn.execute(insert(tables.comments).values(comments).returning(tables.comments)).all()
    conn.commit()
    inserted = [domain.Comment(**row._mapping) for row in inserted]
    return inserted

def create_follows_for_tests(conn: Connection, users: list[domain.User]) -> list[domain.Follow]:
    follows = []
    for u1 in users:
        for u2 in users:
            if u1.id != u2.id:
                follows.append(domain.Follow(follower_id=u1.id, leader_id=u2.id).model_dump(exclude_none=True))
    inserted = conn.execute(insert(tables.follows).values(follows).returning(tables.follows)).all()
    conn.commit()
    inserted = [domain.Follow(**row._mapping) for row in inserted]
    return inserted