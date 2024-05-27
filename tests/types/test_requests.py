from src.types import requests
import pytest
from ulid import ULID

def gen_ulid_as_uuid_str():
    return str(ULID().to_uuid4())

@pytest.mark.parametrize("params,should_succeed", [
    ([gen_ulid_as_uuid_str(), gen_ulid_as_uuid_str(), "new-task"], True),
    ([None, None, "new-task"], False),
    ([gen_ulid_as_uuid_str(), gen_ulid_as_uuid_str(), ""], False),
])
def test_NewTaskRequest(params, should_succeed):
    keys = ('user_id', 'goal_id', 'description')
    params_dict = dict(zip(keys, params))
    if should_succeed:
        requests.NewTask(**params_dict)
    else:
        with pytest.raises(ValueError):
            requests.NewTask(**params_dict)
