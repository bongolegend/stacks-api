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


def create_reactions_for_tests(conn: Connection, user: domain.User, goals: list[domain.Goal], count = 2) -> list[domain.Reaction]:
    reactions = []
    for g in goals:
        for i in range(count):
            reactions.append(domain.Reaction(user_id=user.id, goal_id=g.id, reaction={
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

def create_comments_for_tests(conn: Connection, user: domain.User, goals: list[domain.Goal], count = 2) -> list[domain.Comment]:
    comments = []
    for g in goals:
        for i in range(count):
            comments.append(domain.Comment(user_id=user.id, goal_id=g.id, comment="comment").model_dump(exclude_none=True))
    inserted = conn.execute(insert(tables.comments).values(comments).returning(tables.comments)).all()
    conn.commit()
    inserted = [domain.Comment(**row._mapping) for row in inserted]
    return inserted