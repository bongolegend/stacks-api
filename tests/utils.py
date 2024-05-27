from sqlalchemy import MetaData
from sqlalchemy.orm import Session
from ulid import ULID

from src import api
from src.types import requests
from src.postgres.connection import SessionLocal
from src.postgres import models

def delete_all_entries_from_db():
    session = SessionLocal()
    metadata = MetaData()
    metadata.reflect(bind=session.bind)
    try:
        for table in reversed(metadata.sorted_tables):
            if table.name not in ("alembic_version",):
                session.execute(table.delete())
        session.commit()
    except Exception as e:
        session.rollback()
        raise e
    session.close()


def create_users_for_tests(db : Session, count=2) -> tuple[models.User]:
    users = []
    for i in range(count):
        users.append(models.User(
            id=ULID().to_uuid4(),
            username=f"user{i}",
            email=f"u{i}@a.b"))
    db.add_all(users)
    db.commit()
    _ = [db.refresh(u) for u in users]
    return tuple(users)
