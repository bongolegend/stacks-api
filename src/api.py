from collections import defaultdict
from uuid import UUID

from sqlalchemy import select, insert, delete, and_, or_, desc, update, case, union
from sqlalchemy.engine import Connection

from src.sqlalchemy import tables, utils
from src.types import domain, requests

# exclude these fields from create functions
EXCLUDED_FIELDS = {"created_at", "updated_at"}

### USER

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

def read_followers(conn: Connection, leader_id: UUID) -> list[domain.User]:
    stmt = select(tables.users) \
        .select_from(tables.users) \
        .join(tables.follows, tables.users.c.id == tables.follows.c.follower_id) \
        .where(tables.follows.c.leader_id == leader_id)
    result = conn.execute(stmt).all()
    followers = [domain.User(**row._mapping) for row in result]
    return followers

def read_leaders(conn: Connection, follower_id: UUID) -> list[domain.User]:
    stmt = select(tables.users) \
        .select_from(tables.users) \
        .join(tables.follows, tables.users.c.id == tables.follows.c.leader_id) \
        .where(tables.follows.c.follower_id == follower_id)
    result = conn.execute(stmt).all()
    leaders = [domain.User(**row._mapping) for row in result]
    return leaders

def delete_user(conn: Connection, user_id: UUID) -> None:
    stmt = delete(tables.users).where(tables.users.c.id == user_id)
    conn.execute(stmt)

### FOLLOW

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

### GOAL

def create_goal(conn: Connection, goal: domain.Goal) -> domain.Goal:
    stmt = insert(tables.goals).values(**goal.model_dump(exclude=EXCLUDED_FIELDS, exclude_none=True)).returning(tables.goals)
    inserted = conn.execute(stmt).fetchone()
    return domain.Goal(**inserted._mapping)

def read_goals(conn: Connection, user_id: UUID) -> list[domain.Goal]:
    stmt = select(tables.goals).where(tables.goals.c.user_id == user_id)
    result = conn.execute(stmt).all()
    goals = [domain.Goal(**row._mapping) for row in result]
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

### TASK

def create_task(conn: Connection, task: domain.Task) -> domain.Task:
    stmt = insert(tables.tasks).values(**task.model_dump(exclude=EXCLUDED_FIELDS, exclude_none=True)).returning(tables.tasks)
    inserted = conn.execute(stmt).fetchone()
    return domain.Task(**inserted._mapping)

def read_tasks(conn: Connection, user_id: UUID = None, goal_id: UUID = None) -> list[domain.Task]:
    if [user_id, goal_id].count(None) != 1:
        raise Exception("You must specify exactly one of `user_id`, `goal_id`")
    if user_id:
        filter = tables.tasks.c.user_id == user_id
    elif goal_id:
        filter = tables.tasks.c.goal_id == goal_id
    stmt = select(tables.tasks).where(filter)
    result = conn.execute(stmt).all()
    if not result:
        return []
    tasks = [domain.Task(**row._mapping) for row in result]
    return tasks

def update_task(conn: Connection, task_id: UUID, updates: requests.UpdateTask) -> domain.Task:
    stmt = (
        update(tables.tasks)
        .where(tables.tasks.c.id == task_id)
        .values(**updates.model_dump(exclude_none=True))
        .returning(tables.tasks))
    updated = conn.execute(stmt).fetchone()
    return domain.Task(**updated._mapping)

def delete_task(conn: Connection, task_id: UUID) -> None:
    stmt = delete(tables.tasks).where(tables.tasks.c.id == task_id)
    conn.execute(stmt)

### REACTION

def create_reaction(conn: Connection, reaction: domain.Reaction) -> domain.Reaction:
    stmt = (
        insert(tables.reactions)
        .values(**reaction.model_dump(exclude=EXCLUDED_FIELDS, exclude_none=True))
        .returning(tables.reactions))
    inserted = conn.execute(stmt).fetchone()
    return domain.Reaction(**inserted._mapping)

def read_reactions(conn: Connection, user_id: UUID) -> list[domain.Reaction]:
    stmt = select(tables.reactions).where(tables.reactions.c.user_id == user_id)
    result = conn.execute(stmt).all()
    reactions = [domain.Reaction(**row._mapping) for row in result]
    return reactions

def delete_reaction(conn: Connection, reaction_id: UUID) -> None:
    stmt = delete(tables.reactions).where(tables.reactions.c.id == reaction_id)
    conn.execute(stmt)

### TIMELINE

def generate_timeline_of_leaders(conn: Connection, follower_id: UUID, count: int = 20) -> list[domain.Post]:  
    """This also includes the posts of the follower_id"""
    goals = _generate_timeline_of_leaders(conn, tables.goals, follower_id, count)
    tasks = _generate_timeline_of_leaders(conn, tables.tasks, follower_id, count)
    posts = sorted(goals + tasks, key=lambda post: post.sort_on, reverse=True)
    return posts


def _generate_timeline_of_leaders(conn: Connection, table, follower_id: UUID, count: int = 20) -> list[domain.Post]:
    """table must be either `goals` or `tasks`"""
    U_ = "u_"

    if table == tables.goals:
        reaction_foreign_key = tables.reactions.c.goal_id
    elif table == tables.tasks:
        reaction_foreign_key = tables.reactions.c.task_id
    else:
        raise ValueError("table must be either `goals` or `tasks`")

    base_query = (select(*utils.prefix(tables.users, U_),
                  table,
                  table.c.created_at.label("sort_on"))
                  .select_from(tables.users)
                  .join(table))
    
    leaders_query = (base_query
                        .join(tables.follows, tables.users.c.id == tables.follows.c.leader_id)
                        .where(tables.follows.c.follower_id == follower_id))
    
    self_query = (base_query
                    .where(table.c.user_id == follower_id))

    union_query = union(leaders_query, self_query).order_by(desc("sort_on")).limit(count)

    primary_result = conn.execute(union_query).all()

    reactions_query = (select(tables.reactions)
                       .join(table, reaction_foreign_key == table.c.id)
                       .where(reaction_foreign_key.in_([row.id for row in primary_result])))

    reactions_result = conn.execute(reactions_query).all()

    reactions = defaultdict(list)
    for row in reactions_result:
        key = row.goal_id or row.task_id
        reactions[key].append(domain.Reaction(**row._mapping))

    posts = [
        domain.Post(
            user=utils.filter_by_prefix(row, U_),
            primary={**row._mapping, "table": table.name},
            reactions=reactions.get(row.id, []),
            sort_on=row.sort_on
        )
        for row in primary_result
    ]
    return posts
