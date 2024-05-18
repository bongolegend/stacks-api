from sqlalchemy import Column, BigInteger, String, Text, Boolean, DateTime, ForeignKey, Identity
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship

Base = declarative_base()

class CommonBase(Base):
    __abstract__ = True
    id = Column(BigInteger, Identity(), primary_key=True)
    created_at = Column(DateTime(timezone=True))
    updated_at = Column(DateTime(timezone=True))

class User(CommonBase):
    __tablename__ = 'users'

    username = Column(String, unique=True, nullable=False)
    email = Column(String, unique=True, nullable=False)

    tasks = relationship('Task', back_populates='user', cascade="all, delete", passive_deletes=True)
    goals = relationship('Goal', back_populates='user', cascade="all, delete", passive_deletes=True)

class Task(CommonBase):
    __tablename__ = 'tasks'

    title = Column(String, nullable=False)
    description = Column(Text, nullable=True)
    due_date = Column(DateTime(timezone=True), nullable=False)
    is_completed = Column(Boolean, default=False)

    user_id = Column(BigInteger, ForeignKey('users.id', ondelete="CASCADE"), nullable=False)
    goal_id = Column(BigInteger, ForeignKey('goals.id'), nullable=True)

    user = relationship('User', back_populates='tasks')
    goal = relationship('Goal', back_populates='tasks')

class Goal(CommonBase):
    __tablename__ = 'goals'

    title = Column(String, nullable=False)
    description = Column(Text, nullable=True)
    due_date = Column(DateTime(timezone=True), nullable=False)
    is_completed = Column(Boolean, default=False)

    user_id = Column(BigInteger, ForeignKey('users.id', ondelete="CASCADE"), nullable=False)

    user = relationship('User', back_populates='goals')
    tasks = relationship('Task', back_populates='goal')