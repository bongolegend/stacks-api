from sqlalchemy import MetaData, Table, Column, String, Text, Boolean, DateTime, ForeignKey, func, text
from sqlalchemy.dialects.postgresql import UUID

metadata = MetaData()


users = Table(
    'users', metadata,
    Column('id', UUID(as_uuid=True), primary_key=True, server_default=text("uuid_generate_v4()")),
    Column('username', String, unique=True, nullable=False),
    Column('email', String, unique=True, nullable=False),
    Column('created_at', DateTime(timezone=True), server_default=func.now()),
    Column('updated_at', DateTime(timezone=True), server_default=func.now(), onupdate=func.now())
)

follows = Table(
    'follows', metadata,
    Column('follower_id', UUID(as_uuid=True), ForeignKey('users.id', ondelete="CASCADE"), primary_key=True),
    Column('leader_id', UUID(as_uuid=True), ForeignKey('users.id', ondelete="CASCADE"), primary_key=True),
    Column('created_at', DateTime(timezone=True), server_default=func.now()),
    Column('updated_at', DateTime(timezone=True), server_default=func.now(), onupdate=func.now())
)

goals = Table(
    'goals', metadata,
    Column('id', UUID(as_uuid=True), primary_key=True, server_default=text("uuid_generate_v4()")),
    Column('user_id', UUID(as_uuid=True), ForeignKey('users.id', ondelete="CASCADE"), nullable=False),
    Column('description', Text, nullable=False),
    Column('is_completed', Boolean, default=False),
    Column('created_at', DateTime(timezone=True), server_default=func.now()),
    Column('updated_at', DateTime(timezone=True), server_default=func.now(), onupdate=func.now())
)

tasks = Table(
    'tasks', metadata,
    Column('id', UUID(as_uuid=True), primary_key=True, server_default=text("uuid_generate_v4()")),
    Column('user_id', UUID(as_uuid=True), ForeignKey('users.id', ondelete="CASCADE"), nullable=False),
    Column('goal_id', UUID(as_uuid=True), ForeignKey('goals.id'), nullable=False),
    Column('description', Text, nullable=False),
    Column('is_completed', Boolean, default=False),
    Column('created_at', DateTime(timezone=True), server_default=func.now()),
    Column('updated_at', DateTime(timezone=True), server_default=func.now(), onupdate=func.now())
)
