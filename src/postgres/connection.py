import sqlalchemy
from contextlib import contextmanager
from sqlalchemy.orm import sessionmaker

SQLALCHEMY_DATABASE_URL = "postgresql://admin:password@postgres/stacks"
engine = sqlalchemy.create_engine(SQLALCHEMY_DATABASE_URL)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

@contextmanager
def get_db():
    session = SessionLocal()
    try:
        yield session
    finally:
        session.close()
