from typing import AsyncGenerator
from contextlib import asynccontextmanager

from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse

from app.core.db import engine
from app.endpoints import main_router
from app.endpoints.token import get_token_router
from fastapi_utilities import repeat_every

from app.config import TASK_FREQUENCY_IN_SECONDS, logger
from app.endpoints.utils import trigger_round_robin_assignment


@asynccontextmanager
async def lifespan(_: FastAPI) -> AsyncGenerator:
    """
    Handling events before and after FastAPI startup
    """
    await auto_trigger_assignment()
    yield
    """
    Dispose of all active database connections once the server is shutdown
    """
    engine.dispose()


@repeat_every(seconds=TASK_FREQUENCY_IN_SECONDS)
async def auto_trigger_assignment():
    logger.info("Running round robin")
    await trigger_round_robin_assignment()


app = FastAPI(lifespan=lifespan)


@app.exception_handler(Exception)
async def general_exception_handler(request: Request, exc: Exception) -> JSONResponse:
    return JSONResponse(
        status_code=500,
        content={"message": "An unexpected error occurred. Please try again later."},
    )


app.include_router(main_router)
app.include_router(get_token_router)
