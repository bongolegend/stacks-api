from src.types import domain
import pytest


def test_init_Brick():
    u = domain.User(email="a@b.c", username="adc")
    g = domain.Goal(user_id=u.id, description="goal")
    t = domain.Task(user_id=u.id, goal_id=g.id, description="task")
    
    # succeeds
    domain.Brick(user=u, primary=g)
    domain.Brick(user=u, primary=t, secondary=g)

    with pytest.raises(ValueError):
        domain.Brick(user=u, primary=t)
    with pytest.raises(ValueError):
        domain.Brick(user=u, primary=g, secondary=g)