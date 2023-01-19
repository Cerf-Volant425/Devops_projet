#!/usr/bin/env python3

import uvicorn

from fastapi import Depends, FastAPI, HTTPException
from starlette.responses import Response
from fastapi.logger import logger

from starlette.requests import Request
from starlette.middleware.cors import CORSMiddleware
from pydantic import BaseModel,BaseSettings
from typing import List
import pymongo
import requests
from models import Dname, Photographer, PhotographerDesc, PHOTOGRAPHER_BODY, Photographers, PhotographerDigest

from beanie import Document, init_beanie
import asyncio, motor

import re

class Settings(BaseSettings):
    mongo_host: str = "localhost"
    mongo_port: str = "27017"
    mongo_user: str = ""
    mongo_password: str = ""
    database_name: str = "photographers"
    auth_database_name: str = "photographers"

settings = Settings()

app = FastAPI(title = "Photographer Service")

origins = [
    "http://localhost",
    "http://localhost:8080",
    "http://localhost:3000",
    "localhost:3000",
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# FastAPI logging
#gunicorn_logger = logging.getLogger('gunicorn.error')
#logger.handlers = gunicorn_logger.handlers

@app.on_event("startup")
async def startup_event():
    conn = f"mongodb://"
    if settings.mongo_user:
        conn += f"{settings.mongo_user}:{settings.mongo_password}@"
    conn += f"{settings.mongo_host}:{settings.mongo_port}"
    conn += f"/{settings.database_name}?authSource={settings.auth_database_name}"
    client = motor.motor_asyncio.AsyncIOMotorClient(conn)
    await init_beanie(database=client[settings.database_name], document_models=[Photographer])

@app.get("/photographers", response_model = Photographers, status_code = 200)    
async def get_photographers(request: Request, offset: int = 0, limit: int = 10):
    list_of_digests = list()
    last_id = 0
    try:
        async for result in Photographer.find().sort("_id").skip(offset).limit(limit):
            digest = PhotographerDigest(display_name=result.display_name, link="/photographer/" + result.display_name)
            last_id = result.id
            list_of_digests.append(digest)
    except pymongo.errors.ServerSelectionTimeoutError:
        raise HTTPException(status_code=503, detail="Mongo unavailable")
    has_more = await Photographer.find(Photographer.id > last_id).to_list()
    return {'items': list_of_digests, 'has_more': True if len(has_more) else False}

@app.post("/photographers", status_code = 201)
async def create_photographer(response: Response, photographer: PhotographerDesc = PHOTOGRAPHER_BODY):

    try:
        check = await Photographer.find_one(Photographer.display_name == photographer.display_name)
        if check is None:
            await Photographer(**dict(photographer)).insert()
            response.headers["Location"] = "/photographer/" + str(photographer.display_name)
        else:
            raise HTTPException(status_code = 409, detail = "Conflict")
    except pymongo.errors.ServerSelectionTimeoutError:
        raise HTTPException(status_code=503, detail="Mongo unavailable")

@app.get("/photographer/{display_name}", response_model = PhotographerDesc, status_code = 200)    
async def get_photographer(display_name: str = Dname.PATH_PARAM):

    try:
        photographer = await Photographer.find_one(Photographer.display_name == display_name)    
        if photographer is not None:
            return photographer
        else:
            raise HTTPException(status_code = 404, detail = "Photographer does not exist")
    except pymongo.errors.ServerSelectionTimeoutError:
        raise HTTPException(status_code=503, detail="Mongo unavailable")


@app.put("/photographer/{display_name}", status_code = 200)
async def update_photographer(display_name: str = Dname.PATH_PARAM, photographer: PhotographerDesc = PHOTOGRAPHER_BODY):
    try:
        found = await Photographer.find_one(Photographer.display_name == display_name)    
        if found is None:
            raise HTTPException(status_code = 503, detail = "Not Found")
        else:
            await found.set(dict(photographer))
    except pymongo.errors.ServerSelectionTimeoutError:
        raise HTTPException(status_code=503, detail="Mongo unavailable")


@app.delete("/photographer/{display_name}", status_code = 200)
async def delete_photographer(display_name: str = Dname.PATH_PARAM):
    try:
        found = await Photographer.find_one(Photographer.display_name == display_name)    
        if found:
            await found.delete()
        else:
            raise HTTPException(status_code = 503, detail = "Not Found")
    except pymongo.errors.ServerSelectionTimeoutError:
        raise HTTPException(status_code=503, detail="Mongo unavailable")

if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000, log_level="info")
    #logger.setLevel(logging.DEBUG)
else:
    #logger.setLevel(gunicorn_logger.level)
    pass
