from fastapi import FastAPI

from src.routes import common, v0


app = FastAPI()

app.include_router(common.router)
app.include_router(v0.router)
