import logging

from fastapi import FastAPI, Request
from fastapi.exceptions import RequestValidationError
from fastapi.responses import JSONResponse
from fastapi.middleware.cors import CORSMiddleware

from src.routes import common, v0

logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger(__name__)

app = FastAPI()

app.include_router(common.router)
app.include_router(v0.router)

# TODO hide this behind dev
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:8081"],  # Allow specific origins
    allow_credentials=True,
    allow_methods=["*"],  # Allow all HTTP methods
    allow_headers=["*"],  # Allow all headers
)


@app.exception_handler(RequestValidationError)
async def validation_exception_handler(request: Request, exc: RequestValidationError):
    logger.error(f"Validation error: {exc.errors()} - Request: {request.method} {request.url}")
    
    body = await request.json()
    logger.error(f"Request body: {body}")

    return JSONResponse(
        status_code=422,
        content={"detail": exc.errors()},
    )

