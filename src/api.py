from collections import defaultdict
from uuid import UUID

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
        username: str = None, 
        email: str = None) -> domain.User | None:
    if [id, username, email].count(None) != 2:
        raise ValueError("You must pass exactly one of id, username or email")
    if id:
        filter = tables.users.c.id == id
    if username:
        filter = tables.users.c.username == username
    if email:
        filter = tables.users.c.email == email
    stmt = select(tables.users).where(filter)
    result = conn.execute(stmt).fetchone()
    if result is None:
        return
    return domain.User(**result._mapping)

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

def read_goals(conn: Connection, user_id: UUID) -> list[domain.GoalEnriched]:
    primary = tables.goals.alias('primary')
    parent = tables.goals.alias('parent')
    query = (select(
                    *utils.prefix(primary, "primary_"),
                    *utils.prefix(parent, "parent_"),
                    *utils.prefix(tables.users, "u_"))
                  .select_from(primary)
                  .join(tables.users)
                  .outerjoin(parent, primary.c.parent_id == parent.c.id)
                  .where(primary.c.user_id == user_id))
    
    result = conn.execute(query).all()

    goals = [domain.GoalEnriched(
                user=utils.filter_by_prefix(row, "u_"),
                parent=domain.Goal(**utils.filter_by_prefix(row, "parent_")) if row.primary_parent_id else None,
                **utils.filter_by_prefix(row, "primary_")
                )
            for row in result]
    
    return goals

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

def read_reactions(conn: Connection, user_id: UUID = None, goal_id: UUID = None) -> list[domain.Reaction]:
    if [user_id, goal_id].count(None) != 1:
        raise ValueError("You must pass exactly one of user_id, goal_id")
    if goal_id:
        filter = tables.reactions.c.goal_id == goal_id
    elif user_id:
        filter = tables.reactions.c.user_id == user_id
    stmt = select(tables.reactions).where(filter)
    result = conn.execute(stmt).all()
    reactions = [domain.Reaction(**row._mapping) for row in result]
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

### ANNOUNCEMENTS

def generate_announcements(conn: Connection, follower_id: UUID, count: int = 20) -> list[domain.Announcement]:
    primary = tables.goals.alias('primary')
    parent = tables.goals.alias('parent')

    base_query = (select(
                    primary.c.id,
                    *utils.prefix(primary, "primary_"),
                    *utils.prefix(parent, "parent_"),
                    *utils.prefix(tables.users, "u_"),
                    primary.c.updated_at.label("sort_on"))
                  .select_from(primary)
                  .join(tables.users)
                  .outerjoin(parent, primary.c.parent_id == parent.c.id))
    
    leaders_query = (base_query
                        .join(tables.follows, tables.users.c.id == tables.follows.c.leader_id)
                        .where(tables.follows.c.follower_id == follower_id))
    
    self_query = (base_query
                    .where(primary.c.user_id == follower_id))

    union_query = union(leaders_query, self_query).order_by(desc("sort_on")).limit(count)

    result = conn.execute(union_query).all()

    reactions = _read_reactions_or_comments(conn, result, tables.reactions, domain.Reaction)
    comments = _read_reactions_or_comments(conn, result, tables.comments, domain.Comment)

    announcements = []
    for row in result:
        if row.primary_parent_id is None:
            parent = None
        else:
            parent = domain.Goal(**utils.filter_by_prefix(row, "parent_"))
        announcements.append(domain.Announcement(
            id=row.id,
            user=utils.filter_by_prefix(row, "u_"),
            goal=utils.filter_by_prefix(row, "primary_"),
            parent=parent,
            reactions=reactions.get(row.id, []),
            comment_count=len(comments.get(row.id, [])),
            sort_on=row.sort_on
        ))

    return announcements


def _read_reactions_or_comments(
        conn: Connection, primary_result: list[Row], 
        secondary_table: Table, result_type: domain.Reaction | domain.Comment
        ) -> dict[UUID, list[domain.Reaction | domain.Comment]]:

    query = (select(secondary_table)
                       .join(tables.goals, secondary_table.c.goal_id == tables.goals.c.id)
                       .where(secondary_table.c.goal_id.in_([row.id for row in primary_result])))

    result = conn.execute(query).all()

    secondaries = defaultdict(list)
    for row in result:
        secondaries[row.goal_id].append(result_type(**row._mapping))
    return secondaries