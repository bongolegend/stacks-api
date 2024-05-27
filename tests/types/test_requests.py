from src.types import requests
import pytest
from ulid import ULID

@pytest.mark.parametrize("params,should_succeed", [
    ([str(ULID()), str(ULID()), "new-task"], True),
    ([str(ULID()), None, "new-task"], True),
    ([None, None, "new-task"], False),
    ([str(ULID()), str(ULID()), ""], False),
])
def test_NewTaskRequest(params, should_succeed):
    keys = ('user_id', 'goal_id', 'description')
    params_dict = dict(zip(keys, params))
    if should_succeed:
        requests.NewTaskRequest(**params_dict)
    else:
        with pytest.raises(ValueError):
            requests.NewTaskRequest(**params_dict)
