from src import api
from src.types import domain, requests
from tests import utils


def test_create_read_delete_user(commit_as_you_go):
    db_user = api.create_user(commit_as_you_go, domain.User(username='user1', email='u1@a.b'))
    commit_as_you_go.commit()
    assert api.read_user(commit_as_you_go, id=db_user.id) == db_user
    api.delete_user(commit_as_you_go, db_user.id)
    commit_as_you_go.commit()

    assert api.read_user(commit_as_you_go, id=db_user.id) is None

def test_search_users(commit_as_you_go):
    u0, u1, u2 = utils.create_users_for_tests(commit_as_you_go, count=3)
    api.create_follow(commit_as_you_go, domain.Follow(follower_id=u0.id, leader_id=u1.id))
    # this follow should not affect the search from the perspective of u0
    api.create_follow(commit_as_you_go, domain.Follow(follower_id=u2.id, leader_id=u1.id))

    commit_as_you_go.commit()
    s_users = api.search_users(commit_as_you_go, u0.id)
    assert len(s_users) == 2
    s_u1 = next(filter(lambda u: u.id == u1.id, s_users))
    s_u2 = next(filter(lambda u: u.id == u2.id, s_users))
    assert s_u1.leader == True
    assert s_u2.leader == False


from insert_fixtures import insert_data

def test_search_users_with_unknown_edge_case(commit_as_you_go):
    s_users = insert_data()
    u0 = s_users[0]

    searched_users = api.search_users(commit_as_you_go, u0.id)
    assert len(searched_users) == len(s_users) - 1


def test_read_followers_and_leaders(commit_as_you_go):
    u0, u1, u2 = utils.create_users_for_tests(commit_as_you_go, count=3)
    api.create_follow(commit_as_you_go, domain.Follow(follower_id=u1.id, leader_id=u0.id))
    api.create_follow(commit_as_you_go, domain.Follow(follower_id=u2.id, leader_id=u0.id))
    commit_as_you_go.commit()

    assert api.read_leaders(commit_as_you_go, u1.id) == [u0]
    assert api.read_leaders(commit_as_you_go, u0.id) == []
    assert api.read_followers(commit_as_you_go, u0.id) == [u1, u2]

def test_create_delete_follow(commit_as_you_go):
    u0, u1 = utils.create_users_for_tests(commit_as_you_go)
    follow = domain.Follow(follower_id=u1.id, leader_id=u0.id)
    api.create_follow(commit_as_you_go, follow)
    commit_as_you_go.commit()
    api.delete_follow(commit_as_you_go, follow)

    assert api.read_followers(commit_as_you_go, u0.id) == []

def test_create_read_update_delete_goal(commit_as_you_go):
    u0 = utils.create_users_for_tests(commit_as_you_go, count=1)[0]
    goal = domain.Goal(user_id=u0.id, description="goal-description")
    db_goal = api.create_goal(commit_as_you_go, goal)
    commit_as_you_go.commit()

    assert api.read_goals(commit_as_you_go, u0.id) == [db_goal]

    updates = requests.UpdateGoal(is_completed=True)
    updated_goal = api.update_goal(commit_as_you_go, db_goal.id, updates)
    commit_as_you_go.commit()

    assert updated_goal.is_completed != db_goal.is_completed
    assert updated_goal.created_at == db_goal.created_at
    assert updated_goal.updated_at > db_goal.updated_at

    api.delete_goal(commit_as_you_go, db_goal.id)
    commit_as_you_go.commit()

    assert api.read_goals(commit_as_you_go, u0.id) == []

def test_create_read_update_delete_task(commit_as_you_go):
    u0 = utils.create_users_for_tests(commit_as_you_go, count=1)[0]
    g0 = utils.create_goals_for_tests(commit_as_you_go, [u0], count=1)[0]
    task = domain.Task(user_id=u0.id, goal_id=g0.id, description="task-description")
    db_task = api.create_task(commit_as_you_go, task)
    commit_as_you_go.commit()

    assert api.read_tasks(commit_as_you_go, u0.id) == [db_task]

    updates = requests.UpdateTask(is_completed=True)
    updated_task = api.update_task(commit_as_you_go, db_task.id, updates)
    commit_as_you_go.commit()

    assert updated_task.is_completed != db_task.is_completed
    assert updated_task.created_at == db_task.created_at
    assert updated_task.updated_at > db_task.updated_at

    api.delete_task(commit_as_you_go, db_task.id)
    commit_as_you_go.commit()

    assert api.read_tasks(commit_as_you_go, u0.id) == []


def test_create_delete_reaction(commit_as_you_go):
    u0 = utils.create_users_for_tests(commit_as_you_go, count=1)[0]
    g0 = utils.create_goals_for_tests(commit_as_you_go, [u0], count=1)[0]
    t0 = utils.create_tasks_for_tests(commit_as_you_go, [g0], count=1)[0]

    reaction = domain.Reaction(user_id=u0.id, reaction={'reaction': 'value'}, reaction_library='library', task_id=t0.id)
    db_reaction = api.create_reaction(commit_as_you_go, reaction)
    commit_as_you_go.commit()

    assert api.read_reactions(commit_as_you_go, u0.id) == [db_reaction]

    api.delete_reaction(commit_as_you_go, db_reaction.id)
    commit_as_you_go.commit()

    assert api.read_reactions(commit_as_you_go, u0.id) == []

def test_generate_timeline_of_leaders(commit_as_you_go):
    u0, u1, u2 = utils.create_users_for_tests(commit_as_you_go, count=3)
    goals = utils.create_goals_for_tests(commit_as_you_go, users=[u0, u1, u2], count=1)
    reactions = utils.create_reactions_for_tests(commit_as_you_go, u0, goals, count=1)

    api.create_follow(commit_as_you_go, domain.Follow(follower_id=u1.id, leader_id=u0.id))
    api.create_follow(commit_as_you_go, domain.Follow(follower_id=u2.id, leader_id=u0.id))

    commit_as_you_go.commit()
    timeline = api.generate_timeline_of_leaders(commit_as_you_go, u0.id)
    assert len(timeline) == 1
    assert all([len(p.reactions) == 1 for p in timeline])

    timeline2 = api.generate_timeline_of_leaders(commit_as_you_go, u1.id)
    assert len(timeline2) == 2
