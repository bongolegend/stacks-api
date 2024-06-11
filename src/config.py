import yaml
import os

def get_config(env: str = None) -> dict:
    if not env:
        env = os.environ.get('ENV', 'dev')
    with open('./config.yaml', 'r') as f:
        config = yaml.safe_load(f)
    return config[env]
