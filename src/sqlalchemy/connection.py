from sqlalchemy import create_engine
from contextlib import contextmanager
from sqlalchemy.orm import sessionmaker

from src.config import get_config


engine = create_engine(**get_config()["db"])

