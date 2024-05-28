import pytest

from src.postgres.connection import engine
from tests import utils

@pytest.fixture(scope="function", autouse=True)
def setup():
    """
    This fixture runs before every test function.
    """
    utils.delete_all_entries_from_db()

@pytest.fixture(scope="function", autouse=True)
def commit_as_you_go():
    """
    This is a 'Commit as you go' connection. You must call `.commit()` 
    explicitly. A commit will not be called for you when the block exits.
    This type of connection allows us to make multiple commits within the
    connection, which allows us to operate directly on the db.
    """
    with engine.connect() as conn:
        yield conn
