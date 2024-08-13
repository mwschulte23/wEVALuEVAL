from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from contextlib import asynccontextmanager
from loguru import logger
logger.add("debug.log", rotation="1 week")

from .database import init_db

## HACK! ##
# from .search import create_collection, log
# create_collection(log)
##

from .api.v1.task import task_router


@asynccontextmanager
async def lifespan(app: FastAPI):
    init_db()
    yield


app = FastAPI(lifespan=lifespan)
app.include_router(task_router, prefix='/api/v1/task')
# app.include_router(log_router, prefix='/api/v1')

origins = ['http://localhost:5173']
app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)