from collections import defaultdict
from uuid import UUID

from sqlalchemy.dialects.postgresql import insert as pg_insert
from sqlalchemy import select, insert, delete, and_, or_, desc, update, case, union, Table, Row, func, literal
from sqlalchemy.engine import Connection

from src.sqlalchemy import tables, utils
from src.types import domain, requests

# exclude these fields from create functions
EXCLUDED_FIELDS = {"created_at", "updated_at"}

### USERS

def create_user(conn: Connection, user: domain.User) -> domain.User:
    stmt = insert(tables.users).values(**user.model_dump(exclude=EXCLUDED_FIELDS, exclude_none=True)).returning(tables.users)
    inserted = conn.execute(stmt).fetchone()._mapping
    return domain.User(**inserted)

def read_user(
        conn: Connection,
        id: UUID = None,
        firebase_id: str|None = None,
        email: str | None = None
        ) -> domain.User | None:
    if [id, firebase_id, email].count(None) != 2:
        raise ValueError("You must pass exactly one of id, firebase_id or email")
    if id:
        filter = tables.users.c.id == id
    if firebase_id:
        filter = tables.users.c.firebase_id == firebase_id
    if email:
        filter = tables.users.c.email == email
    stmt = select(tables.users).where(filter)
    result = conn.execute(stmt).fetchone()
    if result is None:
        return
    # Filter the result to include only the fields defined in domain.User
    result_without_secrets = {
        key: value for key, value in result._mapping.items() if key in domain.User.model_fields
        }
    return domain.User(**result_without_secrets)

def search_users(conn: Connection, user_id: UUID) -> list[domain.UserEnriched]:
    stmt = (
        select(tables.users, 
               case((tables.follows.c.leader_id == None, False),
                    else_=True).label('leader'))
        .select_from(tables.users)
        .outerjoin(tables.follows, 
                   (tables.users.c.id == tables.follows.c.leader_id) 
                   & (tables.follows.c.follower_id == user_id))
        .where(tables.users.c.id != user_id)
        )
    result = conn.execute(stmt).all()
    users = [domain.UserEnriched(**row._mapping) for row in result]
    return users

def read_followers(conn: Connection, leader_id: UUID) -> list[domain.UserEnriched]:
    '''find all of the followers, and determine if they are also a leader'''
    f0 = tables.follows.alias('f0')
    f1 = tables.follows.alias('f1')
    stmt = (
        select(tables.users,
               literal(True).label('follower'),
               case((f1.c.leader_id == None, False),
                    else_=True).label('leader'))
        .select_from(tables.users)
        .join(f0, f0.c.follower_id == tables.users.c.id)
        .outerjoin(f1, (f1.c.leader_id == tables.users.c.id) & (f1.c.follower_id == leader_id))
        .where(f0.c.leader_id == leader_id))

    result = conn.execute(stmt).all()
    users = [domain.UserEnriched(**row._mapping) for row in result]
    return users


def read_leaders(conn: Connection, follower_id: UUID) -> list[domain.UserEnriched]:
    stmt = select(tables.users) \
        .select_from(tables.users) \
        .join(tables.follows, tables.users.c.id == tables.follows.c.leader_id) \
        .where(tables.follows.c.follower_id == follower_id)
    result = conn.execute(stmt).all()
    leaders = [domain.UserEnriched(leader=True, **row._mapping) for row in result]
    return leaders

def delete_user(conn: Connection, user_id: UUID) -> None:
    stmt = delete(tables.users).where(tables.users.c.id == user_id)
    conn.execute(stmt)

### FOLLOWS

def create_follow(conn: Connection, follow: domain.Follow) -> domain.Follow:
    stmt = insert(tables.follows) \
        .values(**follow.model_dump(exclude=EXCLUDED_FIELDS)) \
        .returning(tables.follows)
    follow = conn.execute(stmt).fetchone()
    return domain.Follow(**follow._mapping)

def delete_follow(conn: Connection, follow: domain.Follow) -> None:
    stmt = delete(tables.follows).where(
        and_(tables.follows.c.follower_id == follow.follower_id,
             tables.follows.c.leader_id == follow.leader_id))
    conn.execute(stmt)

def read_follow_counts(conn: Connection, user_id: UUID) -> domain.FollowCounts:
    stmt = (
        select(
            case((tables.follows.c.follower_id == user_id, "leaders"),
                 else_="followers").label("type"),
            func.count().label("count")
        )
        .select_from(tables.follows)
        .where(or_(tables.follows.c.leader_id == user_id,
                   tables.follows.c.follower_id == user_id))
        .group_by("type"))
    result = conn.execute(stmt).all()
    
    return domain.FollowCounts(**{row.type: row.count for row in result})

### GOALS

def create_goal(conn: Connection, goal: domain.Goal) -> domain.Goal:
    stmt = insert(tables.goals).values(**goal.model_dump(exclude=EXCLUDED_FIELDS, exclude_none=True)).returning(tables.goals)
    inserted = conn.execute(stmt).fetchone()
    return domain.Goal(**inserted._mapping)

def read_goals(
        conn: Connection, 
        user_id: UUID = None, 
        goal_ids: list[UUID] = None, 
        announcements_only: bool = False
    ) -> list[domain.GoalEnriched]:
    primary = tables.goals.alias('primary')
    parent = tables.goals.alias('parent')

    if [user_id, goal_ids].count(None) != 1:
        raise ValueError("You must pass exactly one of user_id or goal_ids")
    if user_id:
        filter = primary.c.user_id == user_id
    if goal_ids:
        filter = primary.c.id.in_(goal_ids)

    query = (select(
                    *utils.prefix(primary, "primary_"),
                    *utils.prefix(parent, "parent_"),
                    *utils.prefix(tables.users, "u_"))
                  .select_from(primary)
                  .join(tables.users)
                  .outerjoin(parent, primary.c.parent_id == parent.c.id)
                  .where(filter))
    
    result = conn.execute(query).all()

    goals = []
    for row in result:
        condition = True
        if announcements_only:
            condition = row.primary_parent_id is None or row.primary_is_completed
        if condition:
            goals.append(domain.GoalEnriched(
                user=utils.filter_by_prefix(row, "u_"),
                parent=domain.Goal(**utils.filter_by_prefix(row, "parent_")) if row.primary_parent_id else None,
                **utils.filter_by_prefix(row, "primary_")
                ))
    
    return goals

def read_announcements(conn: Connection, user_id: UUID) -> list[domain.GoalEnriched]:
    announcements = read_goals(conn, user_id, announcements_only=True)
    leaders = read_leaders(conn, user_id)
    for leader in leaders:
        announcements += read_goals(conn, leader.id, announcements_only=True)
    return announcements

def update_goal(conn: Connection, goal_id: UUID, updates: requests.UpdateGoal) -> domain.Goal:
    stmt = (
        update(tables.goals)
        .where(tables.goals.c.id == goal_id)
        .values(**updates.model_dump(exclude_none=True))
        .returning(tables.goals))
    updated = conn.execute(stmt).fetchone()
    return domain.Goal(**updated._mapping)

def delete_goal(conn: Connection, goal_id: UUID) -> None:
    stmt = delete(tables.goals).where(tables.goals.c.id == goal_id)
    conn.execute(stmt)


### REACTIONS

def create_reaction(conn: Connection, reaction: domain.Reaction) -> domain.Reaction:
    stmt = (
        insert(tables.reactions)
        .values(**reaction.model_dump(exclude=EXCLUDED_FIELDS, exclude_none=True))
        .returning(tables.reactions))
    inserted = conn.execute(stmt).fetchone()
    return domain.Reaction(**inserted._mapping)

def read_reactions(conn: Connection, goal_ids: list[UUID]) -> dict[UUID, list[domain.Reaction]]:
    stmt = select(tables.reactions).where(tables.reactions.c.goal_id.in_(goal_ids))
    result = conn.execute(stmt).all()
    reactions = defaultdict(list)
    for row in result:
        reactions[row.goal_id].append(domain.Reaction(**row._mapping))
    return reactions

def delete_reaction(conn: Connection, reaction_id: UUID) -> None:
    stmt = delete(tables.reactions).where(tables.reactions.c.id == reaction_id)
    conn.execute(stmt)


### COMMENTS

def create_comment(conn: Connection, comment: domain.Comment) -> domain.Comment:
    stmt = (
        insert(tables.comments)
        .values(**comment.model_dump(exclude=EXCLUDED_FIELDS, exclude_none=True))
        .returning(tables.comments))
    inserted = conn.execute(stmt).fetchone()
    return domain.Comment(**inserted._mapping)

def read_comments(conn: Connection, user_id: UUID = None, goal_id: UUID = None) -> list[domain.CommentEnriched]:

    if [user_id, goal_id].count(None) != 1:
        raise ValueError("You must pass exactly one of user_id, goal_id")
    if user_id:
        filter = tables.comments.c.user_id == user_id
    elif goal_id:
        filter = tables.comments.c.goal_id == goal_id
    
    stmt = (
        select(tables.comments, *utils.prefix(tables.users, "u_"))
        .join(tables.users)
        .where(filter))
    result = conn.execute(stmt).all()
    comments = [
        domain.CommentEnriched(
            user=utils.filter_by_prefix(row, "u_"),
            **row._mapping)
        for row in result]
    return comments

def delete_comment(conn: Connection, comment_id: UUID) -> None:
    stmt = delete(tables.comments).where(tables.comments.c.id == comment_id)
    conn.execute(stmt)

def read_comment_count(conn: Connection, goal_id: UUID) -> domain.CommentCount:
    stmt = select(func.count()).select_from(tables.comments).where(tables.comments.c.goal_id == goal_id)
    result = conn.execute(stmt).scalar()
    return domain.CommentCount(goal_id=goal_id, count=result)

def read_comment_counts(conn: Connection, goal_ids: list[UUID]) -> list[domain.CommentCount]:
    stmt = (
        select(tables.comments.c.goal_id, func.count())
        .select_from(tables.comments)
        .where(tables.comments.c.goal_id.in_(goal_ids))
        .group_by(tables.comments.c.goal_id))
    result = conn.execute(stmt).all()
    counts = [domain.CommentCount(goal_id=row.goal_id, count=row.count) for row in result]
    return counts

### COMMENT SUBS AND UNREAD COMMENTS

def create_comment_sub(conn: Connection, comment_sub: domain.CommentSub) -> domain.CommentSub:
    stmt = (
        pg_insert(tables.comment_subs)
        .values(**comment_sub.model_dump(exclude=EXCLUDED_FIELDS, exclude_none=True))
        .on_conflict_do_nothing(constraint='uq_user_goal')
        .returning(tables.comment_subs))
    inserted = conn.execute(stmt).fetchone()
    if inserted is None:
        return
    return domain.CommentSub(**inserted._mapping)

def create_unread_comments(conn: Connection, comment: domain.Comment) -> list[domain.UnreadComment]:
    """Create an unread comment for each comment sub."""
    stmt = (
        insert(tables.unread_comments)
        .from_select(
            [tables.unread_comments.c.user_id,
             tables.unread_comments.c.goal_id,
             tables.unread_comments.c.comment_id,
             tables.unread_comments.c.read],
            select(
                tables.comment_subs.c.user_id,
                literal(comment.goal_id),
                literal(comment.id),
                literal(False)
            )
            .select_from(tables.comment_subs)
            .where(tables.comment_subs.c.goal_id == comment.goal_id)
        )
        .returning(tables.unread_comments))

    inserted = conn.execute(stmt).fetchall()
    unread_comments = [domain.UnreadComment(**row._mapping) for row in inserted]
    return unread_comments


def read_unread_comment_count(conn: Connection, user_id: UUID) -> int:
    stmt = (
        select(func.count())
        .select_from(tables.unread_comments)
        .where(tables.unread_comments.c.user_id == user_id)
        .where(tables.unread_comments.c.read == False)
    )
    result = conn.execute(stmt).scalar()
    return result


def update_unread_comments(conn: Connection, user_id: UUID, comment_ids: list[UUID], read: bool = True) -> None:
    stmt = (
        update(tables.unread_comments)
        .values(read=read)
        .where(tables.unread_comments.c.comment_id.in_(comment_ids))
        .where(tables.unread_comments.c.user_id == user_id))

    conn.execute(stmt)


def read_unread_comments(conn: Connection, user_id: UUID) -> list[domain.CommentEnriched]:
    stmt = (
        select(
            tables.comments, 
            *utils.prefix(tables.users, "u_"))
        .join(tables.comments, tables.unread_comments.c.comment_id == tables.comments.c.id)
        .join(tables.users, tables.comments.c.user_id == tables.users.c.id)
        .where(tables.unread_comments.c.user_id == user_id)
        .where(tables.unread_comments.c.read == False))
    result = conn.execute(stmt).all()
    comments = [
        domain.CommentEnriched(
            user=utils.filter_by_prefix(row, "u_"),
            **row._mapping)
        for row in result]
    return comments