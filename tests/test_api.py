from src import api
from src.types import domain
from tests import utils


def test_create_get_delete_user(commit_as_you_go):
    db_user = api.create_user(commit_as_you_go, domain.User(username='user1', email='u1@a.b'))
    commit_as_you_go.commit()
    assert api.get_user(commit_as_you_go, id=db_user.id) == db_user
    api.delete_user(commit_as_you_go, db_user.id)
    commit_as_you_go.commit()

    assert api.get_user(commit_as_you_go, id=db_user.id) is None

def test_get_followers_and_leaders(commit_as_you_go):
    u0, u1, u2 = utils.create_users_for_tests(commit_as_you_go, count=3)
    api.create_follow(commit_as_you_go, domain.Follow(follower_id=u1.id, leader_id=u0.id))
    api.create_follow(commit_as_you_go, domain.Follow(follower_id=u2.id, leader_id=u0.id))
    commit_as_you_go.commit()

    assert api.get_leaders(commit_as_you_go, u1.id) == [u0]
    assert api.get_leaders(commit_as_you_go, u0.id) == []
    assert api.get_followers(commit_as_you_go, u0.id) == [u1, u2]

def test_create_delete_follow(commit_as_you_go):
    u0, u1 = utils.create_users_for_tests(commit_as_you_go)
    follow = domain.Follow(follower_id=u1.id, leader_id=u0.id)
    api.create_follow(commit_as_you_go, follow)
    commit_as_you_go.commit()
    api.delete_follow(commit_as_you_go, follow)

    assert api.get_followers(commit_as_you_go, u0.id) == []

def test_create_get_update_delete_goal(commit_as_you_go):
    u0 = utils.create_users_for_tests(commit_as_you_go, count=1)[0]
    goal = domain.Goal(user_id=u0.id, description="goal-description")
    db_goal = api.create_goal(commit_as_you_go, goal)
    commit_as_you_go.commit()

    assert api.get_goals(commit_as_you_go, u0.id) == [db_goal]

    updated_goal = api.update_goal(commit_as_you_go, db_goal.model_copy(update={"is_completed": True}))
    commit_as_you_go.commit()

    assert updated_goal.is_completed != db_goal.is_completed
    assert updated_goal.created_at == db_goal.created_at
    assert updated_goal.updated_at > db_goal.updated_at

    api.delete_goal(commit_as_you_go, db_goal.id)
    commit_as_you_go.commit()

    assert api.get_goals(commit_as_you_go, u0.id) == []

def test_create_get_update_delete_task(commit_as_you_go):
    u0 = utils.create_users_for_tests(commit_as_you_go, count=1)[0]
    g0 = utils.create_goals_for_tests(commit_as_you_go, [u0], count=1)[0]
    task = domain.Task(user_id=u0.id, goal_id=g0.id, description="task-description")
    db_task = api.create_task(commit_as_you_go, task)
    commit_as_you_go.commit()

    assert api.get_tasks(commit_as_you_go, u0.id) == [db_task]

    updated_task = api.update_task(commit_as_you_go, db_task.model_copy(update={"is_completed": True}))
    commit_as_you_go.commit()

    assert updated_task.is_completed != db_task.is_completed
    assert updated_task.created_at == db_task.created_at
    assert updated_task.updated_at > db_task.updated_at

    api.delete_task(commit_as_you_go, db_task.id)
    commit_as_you_go.commit()

    assert api.get_tasks(commit_as_you_go, u0.id) == []

def test_generate_timeline_of_leaders(commit_as_you_go):
    u0, u1, u2 = utils.create_users_for_tests(commit_as_you_go, count=3)
    goals = utils.create_goals_for_tests(commit_as_you_go, users=[u0, u1, u2])
    tasks = utils.create_tasks_for_tests(commit_as_you_go, goals)

    api.create_follow(commit_as_you_go, domain.Follow(follower_id=u0.id, leader_id=u1.id))
    api.create_follow(commit_as_you_go, domain.Follow(follower_id=u0.id, leader_id=u2.id))

    commit_as_you_go.commit()
    timeline = api.generate_timeline_of_leaders(commit_as_you_go, u0.id)
    assert len(timeline) == len(tasks)

    timeline2 = api.generate_timeline_of_leaders(commit_as_you_go, u1.id)
    assert len(timeline2) == 2 * 2 # number of tasks per user
