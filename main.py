from dotenv import dotenv_values, find_dotenv, load_dotenv

load_dotenv(find_dotenv(), override=True)

import logging
import sys
from contextlib import asynccontextmanager
from dataclasses import asdict
from datetime import datetime

import requests
import uvicorn
from fastapi import FastAPI
from fastapi.exceptions import RequestValidationError
from fastapi.middleware.cors import CORSMiddleware
from pytz import timezone
from uvicorn.config import LOGGING_CONFIG

from config.env import Env
from core import middlewares
from core.exceptions import handlers as exception_handlers
from core.exceptions.http import CustomHttpException
from core.logging import logger, setupLogger
from handler import auth_handler

requests.packages.urllib3.disable_warnings()

# logging config
logging.Formatter.converter = lambda *args: datetime.now(
    tz=timezone(Env.TZ)
).timetuple()
logging.basicConfig(
    level=logging.DEBUG if Env.DEBUG else logging.INFO,
    format="%(asctime)s %(levelname)s: 92m%(message)s",
    datefmt="%d-%m-%Y %H:%M:%S",
)

# setup custom logger
setupLogger()

# default uvicorn logging format
LOGGING_CONFIG["formatters"]["default"][
    "fmt"
] = "%(asctime)s %(levelprefix)s %(message)s"
LOGGING_CONFIG["formatters"]["default"]["datefmt"] = "%d-%m-%Y %H:%M:%S"
# api call format
LOGGING_CONFIG["formatters"]["access"][
    "fmt"
] = '%(asctime)s %(levelprefix)s %(client_addr)s - "%(request_line)s" %(status_code)s'
LOGGING_CONFIG["formatters"]["access"]["datefmt"] = "%d-%m-%Y %H:%M:%S"


@asynccontextmanager
async def lifespan(app: FastAPI):
    # prepare here
    yield


app = FastAPI(
    title="Quickmart API",
    openapi_url=None if Env.PRODUCTION else "/openapi.json",
    docs_url=None if Env.PRODUCTION else "/",
    redoc_url=None if Env.PRODUCTION else "/redoc",
    lifespan=lifespan,
    # swagger_ui_parameters={"docExpansion": "none"},
)

# register exception handlers
app.add_exception_handler(404, exception_handlers.notFoundErrHandler)
app.add_exception_handler(
    CustomHttpException, exception_handlers.customHttpExceptionHandler
)
app.add_exception_handler(
    RequestValidationError, exception_handlers.reqValidationErrExceptionHandler
)
app.add_exception_handler(RuntimeError, exception_handlers.runTimeErrorHandler)
app.add_exception_handler(Exception, exception_handlers.defaultHttpExceptionHandler)


# register middlewares
app.add_middleware(middlewares.JsonableRespEncoderMiddleware)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# register handlers
app.include_router(auth_handler.AuthRouter)

if __name__ == "__main__":
    # checking unused env ferm .env file
    dotenv_values = dotenv_values(".env")
    required_envs = asdict(Env())
    for key, value in dotenv_values.items():
        if key not in required_envs:
            logger.warning(f"{key} is not defined in required Envs")

    # checking missing env
    for key in required_envs:
        if key not in dotenv_values:
            logger.warning(f"{key} is missing from .env file")

    # process command line argumants (if any)
    args = sys.argv
    if len(args) > 1:
        supported_args = []
        # validate args
        for arg in args[1:]:
            if arg not in supported_args:
                raise Exception(f"unsupported argument: {arg}")

        for arg in args[1:]:
            pass

    uvicorn.run(
        "main:app",
        host=Env.HOST,
        port=Env.PORT,
        reload=Env.RELOAD,
    )
