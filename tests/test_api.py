from src import api
from src.types import requests
from tests import utils


def test_create_get_delete_user(commit_as_you_go):
    db_user = api.create_user(commit_as_you_go, requests.NewUser(username='user1', email='u1@a.b'))
    commit_as_you_go.commit()
    assert api.get_user(commit_as_you_go, id=db_user.id) == db_user
    api.delete_user(commit_as_you_go, db_user.id)
    commit_as_you_go.commit()

    assert api.get_user(commit_as_you_go, id=db_user.id) is None

def test_get_followers_and_leaders(commit_as_you_go):
    u0, u1, u2 = utils.create_users_for_tests(commit_as_you_go, count=3)
    api.create_follow(commit_as_you_go, requests.Follow(follower_id=u1.id, leader_id=u0.id))
    api.create_follow(commit_as_you_go, requests.Follow(follower_id=u2.id, leader_id=u0.id))
    commit_as_you_go.commit()

    assert api.get_leaders(commit_as_you_go, u1.id) == [u0]
    assert api.get_leaders(commit_as_you_go, u0.id) == []
    assert api.get_followers(commit_as_you_go, u0.id) == [u1, u2]

def test_create_delete_follow(commit_as_you_go):
    u0, u1 = utils.create_users_for_tests(commit_as_you_go)
    follow = requests.Follow(follower_id=u1.id, leader_id=u0.id)
    api.create_follow(commit_as_you_go, follow)
    commit_as_you_go.commit()
    api.delete_follow(commit_as_you_go, follow)

    assert api.get_followers(commit_as_you_go, u0.id) == []

def test_create_get_delete_goal(commit_as_you_go):
    u0 = utils.create_users_for_tests(commit_as_you_go, count=1)[0]
    goal = requests.NewGoal(user_id=u0.id, description="goal-description")
    db_goal = api.create_goal(commit_as_you_go, goal)
    commit_as_you_go.commit()

    assert api.get_goals(commit_as_you_go, u0.id) == [db_goal]
    api.delete_goal(commit_as_you_go, db_goal.id)
    commit_as_you_go.commit()

    assert api.get_goals(commit_as_you_go, u0.id) == []

def test_create_get_delete_task(commit_as_you_go):
    u0 = utils.create_users_for_tests(commit_as_you_go, count=1)[0]
    g0 = utils.create_goals_for_tests(commit_as_you_go, [u0], count=1)[0]
    task = requests.NewTask(user_id=u0.id, goal_id=g0.id, description="task-description")
    db_task = api.create_task(commit_as_you_go, task)
    commit_as_you_go.commit()

    assert api.get_tasks(commit_as_you_go, u0.id) == [db_task]
    api.delete_task(commit_as_you_go, db_task.id)
    commit_as_you_go.commit()

    assert api.get_tasks(commit_as_you_go, u0.id) == []
