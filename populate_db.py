from tests import utils
from src.sqlalchemy.connection import engine


def populate_db():
    utils.delete_all_entries_from_db()
    with engine.connect() as conn:
        users = utils.create_users_for_tests(conn, 4)
        goals = utils.create_goals_for_tests(conn, users, 1)
        tasks = utils.create_tasks_for_tests(conn, goals, 2)
        for u in users:
            reactions = utils.create_reactions_for_tests(conn, u, goals, 2)
            comments = utils.create_comments_for_tests(conn, u, goals, 2)
        utils.create_follows_for_tests(conn, users)
        conn.commit()

if __name__ == "__main__":
    populate_db()