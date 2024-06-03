import json
import os
from time import sleep

from sqlalchemy.dialects.postgresql import insert
from src.sqlalchemy import tables
from src.sqlalchemy.connection import engine
from src.types import domain

# Load JSON data
def load_json(file_path):
    with open(file_path, 'r') as file:
        return json.load(file)

# Insert data into tables
def insert_data():
    fixtures_path = 'tests/fixtures'
    user_files = [f for f in os.listdir(fixtures_path) if f.endswith('.json') and 'user' in f]
    follow_file = os.path.join(fixtures_path, 'follows.json')

    with engine.connect() as connection:
        for user_file in user_files:
            data = load_json(os.path.join(fixtures_path, user_file))
            user = domain.User(**data['user'])
            goals = [domain.Goal(**goal) for goal in data['goals']]
            tasks = [domain.Task(**task) for task in data['tasks']]
            
            # Insert user
            connection.execute(insert(tables.users).values(**user.model_dump(exclude_none=True)).on_conflict_do_nothing())
            
            for goal in goals:
                connection.execute(insert(tables.goals).values(**goal.model_dump(exclude_none=True)).on_conflict_do_nothing())
                connection.commit()
            for task in tasks:
                connection.execute(insert(tables.tasks).values(**task.model_dump(exclude_none=True)).on_conflict_do_nothing())
                connection.commit()

        # Insert follows
        follows_data = load_json(follow_file)
        for follow in follows_data['follows']:
            follow = domain.Follow(**follow)
            connection.execute(insert(tables.follows).values(**follow.model_dump(exclude_none=True)).on_conflict_do_nothing())
            connection.commit()

if __name__ == "__main__":
    insert_data()
