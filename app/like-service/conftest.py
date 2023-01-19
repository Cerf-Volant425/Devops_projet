import pytest
import pytest_asyncio
from mongoengine import connect

#from photo import Photo
#from photoId import PhotoId

import motor
from fastapi.testclient import TestClient
from beanie import Document, init_beanie
from model import Like
from pydantic import BaseModel,BaseSettings

@pytest_asyncio.fixture
async def clearLikers():
    await Like.find().delete()

@pytest_asyncio.fixture()
async def initDB():
    class Settings(BaseSettings):
        mongo_host: str = "mongo-service-test"
        mongo_port: str = "27017"
        mongo_user: str = ""
        mongo_password: str = ""
        database_name: str = "likers_test"

    settings = Settings()

    conn = f"mongodb://"
    if settings.mongo_user:
        conn += f"{settings.mongo_user}:{settings.mongo_password}@"
    conn += f"{settings.mongo_host}:{settings.mongo_port}"
    client = motor.motor_asyncio.AsyncIOMotorClient(conn)  # type: ignore
    await init_beanie(database=client["liker-test"], document_models=[Like])
    yield
    # connect("likes", alias="default", host="mongo-service-test")
    # yield
