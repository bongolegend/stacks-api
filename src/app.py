from fastapi import FastAPI

from src.routes import common, v0


app = FastAPI()

app.include_router(common.router)
app.include_router(v0.router)


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)