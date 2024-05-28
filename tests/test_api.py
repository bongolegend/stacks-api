from src import api
from src.types import requests
from tests import utils


def test_create_delete_user(db):
    user = requests.NewUser(username='user1', email='u1@a.b')
    db_user = api.create_user_if_new(db, user)
    api.delete_user(db, db_user.id)

def test_get_user_by_email(db):
    u1 = utils.create_users_for_tests(db, count=1)[0]
    assert api.get_user_by_email(db, email=u1.email) == u1
    assert api.get_user_by_email(db, email='does-not-exist@a.b') is None

def test_create_delete_follow(db):
    u0, u1 = utils.create_users_for_tests(db)
    follow = requests.Follow(follower_id=u0.id, leader_id=u1.id)
    api.create_follow(db, follow)
    assert len(u0.leaders) == 1
    assert len(u0.followers) == 0
    assert len(u1.leaders) == 0
    assert len(u1.followers) == 1

    api.delete_follow(db, follow)
    assert len(u0.leaders) == 0
    assert len(u1.followers) == 0

def test_create_delete_goal(db):
    u0 = utils.create_users_for_tests(db, count=1)[0]
    goal = requests.NewGoal(user_id=u0.id, description="new-goal")
    db_goal = api.create_goal(db, goal)
    api.delete_goal(db, db_goal.id)

def test_create_delete_task(db):
    u0 = utils.create_users_for_tests(db, count=1)[0]
    g0 = utils.create_goals_for_tests(db, (u0,))[0]
    task = requests.NewTask(user_id=g0.user_id, goal_id=g0.id, description="task0")
    db_task = api.create_task(db, task)
    api.delete_task(db, db_task.id)