from sqlalchemy import MetaData, Table, Column, String, Text, Boolean, DateTime, ForeignKey, func, text, UniqueConstraint
from sqlalchemy.dialects.postgresql import UUID, JSONB

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
    Column('updated_at', DateTime(timezone=True), server_default=func.now(), onupdate=func.now()),
    UniqueConstraint('follower_id', 'leader_id', name='uq_follower_leader')
)

goals = Table(
    'goals', metadata,
    Column('id', UUID(as_uuid=True), primary_key=True, server_default=text("uuid_generate_v4()")),
    Column('user_id', UUID(as_uuid=True), ForeignKey('users.id', ondelete="CASCADE"), nullable=False),
    Column('parent_id', UUID(as_uuid=True), ForeignKey('goals.id', ondelete="CASCADE"), nullable=True),
    Column('title', String, nullable=True),
    Column('description', Text, nullable=False),
    Column('due_date', DateTime(timezone=True), nullable=True),
    Column('is_completed', Boolean, default=False),
    Column('created_at', DateTime(timezone=True), server_default=func.now()),
    Column('updated_at', DateTime(timezone=True), server_default=func.now(), onupdate=func.now())
)


reactions = Table(
    'reactions', metadata,
    Column('id', UUID(as_uuid=True), primary_key=True, server_default=text("uuid_generate_v4()")),
    Column('user_id', UUID(as_uuid=True), ForeignKey('users.id', ondelete="CASCADE"), nullable=False),
    Column('goal_id', UUID(as_uuid=True), ForeignKey('goals.id'), nullable=True),
    Column('reaction', JSONB, nullable=False),
    Column('reaction_library', Text, nullable=False),
    Column('created_at', DateTime(timezone=True), server_default=func.now()),
    Column('updated_at', DateTime(timezone=True), server_default=func.now(), onupdate=func.now())
)


comments = Table(
    'comments', metadata,
    Column('id', UUID(as_uuid=True), primary_key=True, server_default=text("uuid_generate_v4()")),
    Column('user_id', UUID(as_uuid=True), ForeignKey('users.id', ondelete="CASCADE"), nullable=False),
    Column('goal_id', UUID(as_uuid=True), ForeignKey('goals.id'), nullable=True),
    Column('comment', Text, nullable=False),
    Column('created_at', DateTime(timezone=True), server_default=func.now()),
    Column('updated_at', DateTime(timezone=True), server_default=func.now(), onupdate=func.now())
)

comment_subs = Table(
    'comment_subs', metadata,
    Column('id', UUID(as_uuid=True), primary_key=True, server_default=text("uuid_generate_v4()")),
    Column('user_id', UUID(as_uuid=True), ForeignKey('users.id', ondelete="CASCADE"), nullable=False),
    Column('goal_id', UUID(as_uuid=True), ForeignKey('goals.id', ondelete="CASCADE"), nullable=False),
    Column('created_at', DateTime(timezone=True), server_default=func.now()),
    Column('updated_at', DateTime(timezone=True), server_default=func.now(), onupdate=func.now()),
    UniqueConstraint('user_id', 'goal_id', name='uq_user_goal')
)

unread_comments = Table(
    'unread_comments', metadata,
    Column('id', UUID(as_uuid=True), primary_key=True, server_default=text("uuid_generate_v4()")),
    Column('user_id', UUID(as_uuid=True), ForeignKey('users.id', ondelete="CASCADE"), nullable=False),
    Column('goal_id', UUID(as_uuid=True), ForeignKey('goals.id', ondelete="CASCADE"), nullable=False),
    Column('comment_id', UUID(as_uuid=True), ForeignKey('comments.id', ondelete="CASCADE"), nullable=False),
    Column('read', Boolean, default=False),
    Column('created_at', DateTime(timezone=True), server_default=func.now()),
    Column('updated_at', DateTime(timezone=True), server_default=func.now(), onupdate=func.now()),
    UniqueConstraint('user_id', 'comment_id', name='uq_user_comment')
)

devices = Table(
    'devices', metadata,
    Column('id', UUID(as_uuid=True), primary_key=True, server_default=text("uuid_generate_v4()")),
    Column('user_id', UUID(as_uuid=True), ForeignKey('users.id', ondelete="CASCADE"), nullable=False),
    Column('os', String, nullable=False),
    Column('version', String, nullable=False),
    Column('expo_push_token', String, nullable=False),
    Column('active', Boolean, default=True),
    Column('created_at', DateTime(timezone=True), server_default=func.now()),
    Column('updated_at', DateTime(timezone=True), server_default=func.now(), onupdate=func.now())
)