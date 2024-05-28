from datetime import datetime

from pydantic import BaseModel

from src.types import requests


class CustomBase(BaseModel):
    created_at: datetime
    updated_at: datetime

class User(CustomBase, requests.NewUser):
    pass

class Goal(CustomBase, requests.NewGoal):
    pass

class Task(CustomBase, requests.NewTask):
    pass

class Follow(requests.Follow):
    pass
    
