from src import main
from src.types import requests
from src.postgres.connection import get_db

def test_create_user():
    user = requests.NewUser(username='user1', email='user1@a.b')
    with get_db() as db:
        db_user = main.create_user_if_new(db, user)
        main.delete_user(db, db_user.id)

def test_get_user_by_email():
    with get_db() as db:
        res = main.get_user_by_email(db, email='does-not-exist@a.b')
        assert res is None

def test_create_follow():
    user1 = requests.NewUser(username='user1', email='user1@a.b')
    user2 = requests.NewUser(username='user2', email='user2@a.b')
    with get_db() as db:
        user1 = main.create_user(db, user1)
        user2 = main.create_user(db, user2)

        follow = requests.Follow(follower_id=user1.id, leader_id=user2.id)
        main.create_follow(db, follow)
        assert len(user1.is_following) == 1
        assert len(user1.followers) == 0
        assert len(user2.is_following) == 0
        assert len(user2.followers) == 1

        main.delete_follow(db, follow)
        main.delete_user(db, user1.id)
        main.delete_user(db, user2.id)