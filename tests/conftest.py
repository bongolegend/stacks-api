import pytest

from src.postgres.connection import get_db
from tests import utils

@pytest.fixture(scope="function", autouse=True)
def setup():
    """
    This fixture runs before every test function.
    """
    utils.delete_all_entries_from_db()

@pytest.fixture(scope="session", autouse=True)
def db():
    with get_db() as db:
        yield db
