from sqlalchemy import create_engine
from contextlib import contextmanager
from sqlalchemy.orm import sessionmaker

SQLALCHEMY_DATABASE_URL = "postgresql://admin:password@postgres/stacks"
engine = create_engine(SQLALCHEMY_DATABASE_URL)

# WARNING: session is for use with the ORM only
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

@contextmanager
def get_db():
    session = SessionLocal()
    try:
        yield session
    finally:
        session.close()
