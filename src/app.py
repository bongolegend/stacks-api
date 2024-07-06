import logging
import structlog

from fastapi import FastAPI, Request
from fastapi.exceptions import RequestValidationError
from fastapi.responses import JSONResponse
from fastapi.middleware.cors import CORSMiddleware

from src.routes import common, v0

log = structlog.get_logger()
log.info("this is a test", key="value!")

app = FastAPI()

app.include_router(common.router)
app.include_router(v0.router)

# TODO hide this behind dev
app.add_middleware(
    CORSMiddleware,
    # allow_origins=["http://localhost:8081", "http://www.getstacks.io"],  # Allow specific origins
    allow_origins=["*"],  # Allow all origins
    allow_credentials=True,
    allow_methods=["*"],  # Allow all HTTP methods
    allow_headers=["*"],  # Allow all headers
)


@app.exception_handler(RequestValidationError)
async def validation_exception_handler(request: Request, exc: RequestValidationError):
    log.error("Validation error", error=exc.errors(), request_method=request.method, request_url=request.url)
    
    body = await request.json()

    log.error("Request body", content=body)

    return JSONResponse(
        status_code=422,
        content={"detail": exc.errors()},
    )

