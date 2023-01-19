#!/usr/bin/env python3

import uvicorn

from fastapi import FastAPI, File, Form, UploadFile, HTTPException
from starlette.responses import Response, StreamingResponse
from starlette.requests import Request
from mongoengine import connect
from pydantic import BaseModel,BaseSettings
from fastapi.logger import logger
import logging
from like_const import REQUEST_TIMEOUT
from model import Dname, Like, LikeDesc, LIKE_BODY, LikeDigest, Likers, Count
from starlette.middleware.cors import CORSMiddleware
import pymongo
from beanie import Document, init_beanie
import asyncio, motor
import requests
import re

class Settings(BaseSettings):
    mongo_host: str = "localhost"
    mongo_port: str = "27017"
    mongo_user: str = ""
    mongo_password: str = ""
    database_name: str = "likes"
    auth_database_name: str = "likes"

    photographer_host: str = "photographer-service"
    photographer_port: str = "80"

    photo_host: str = "photo-service"
    photo_port: str = "80"

settings = Settings()

photographer_service = 'http://' + settings.photographer_host + ':' + settings.photographer_port + '/'
photo_service = 'http://' + settings.photo_host + ':' + settings.photo_port

app = FastAPI(title = "Like Service")

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

@app.on_event("startup")
async def startup_event():
    conn = f"mongodb://"
    if settings.mongo_user:
        conn += f"{settings.mongo_user}:{settings.mongo_password}@"
    conn += f"{settings.mongo_host}:{settings.mongo_port}"
    conn += f"/{settings.database_name}?authSource={settings.auth_database_name}"
    client = motor.motor_asyncio.AsyncIOMotorClient(conn)
    await init_beanie(database=client[settings.database_name], document_models=[Like])

@app.post("/like/{display_name}/{photo_id}", status_code = 201)
async def give_like(response: Response, photo_id: int, display_name: str, like: LikeDesc = LIKE_BODY):  
    
    logger.info("A liker gives a like to a photo ...")
    try:
        liker = requests.get(photographer_service + 'photographer/' + like.liker_name,
                                        timeout=REQUEST_TIMEOUT)
        # Make sure the liker exists
        if liker.status_code == requests.codes.ok: 
            photo = requests.get(f'{photo_service}/photo/{display_name}/{photo_id}',
                                        timeout=REQUEST_TIMEOUT)
            # Make sure the photo exists
            if photo.status_code == requests.codes.ok:
                found = await Like.find_one(Like.liker_name == like.liker_name, Like.photo_id == photo_id)
                # Make sure the liker haven't given a like to this photo
                if found is None:
                    like_given = {'display_name' : display_name, 'liker_name': like.liker_name, 'photo_id' : photo_id, 'date' : like.date}
                    await Like(**(like_given)).insert() 
                    response.headers["Location"] = "/like/" + display_name + '/' + str(photo_id) + '/'+ like.liker_name     # 这里该怎么返回   
                else: 
                    raise HTTPException(status_code = 409, detail = "Conflict! The liker has already liked already this photo...")
            
            elif photo.status_code == requests.codes.unavailable:
                raise HTTPException(status_code = 503, detail = "Mongo unavailable")
            elif photo.status_code == requests.codes.not_found:
                raise HTTPException(status_code = 404, detail = "Photo Not Found")

        elif liker.status_code == requests.codes.unavailable:
            raise HTTPException(status_code = 503, detail = "Mongo unavailable")
        elif photographer.status_code == requests.codes.not_found:
            raise HTTPException(status_code = 404, detail = "Liker Not Found")
            
    except (pymongo.errors.AutoReconnect,
            pymongo.errors.ServerSelectionTimeoutError,
            pymongo.errors.NetworkTimeout) as e:
        raise HTTPException(status_code = 503, detail = "Mongo unavailable")


@app.get("/like/{display_name}/{photo_id}", response_model = Likers, status_code = 200)
async def get_photo_all_likers(photo_id: int, display_name: str):
    logger.info("Get all the likers who give like to a photo ...")

    list_of_digests = list()
    try:
        photo = requests.get(f'{photo_service}/photo/{display_name}/{photo_id}',
                                        timeout=REQUEST_TIMEOUT)
        # Make sure the photo exists
        if photo.status_code == requests.codes.ok:
            async for result in Like.find(Like.photo_id == photo_id, Like.display_name == display_name):
                digest = LikeDigest(display_name = result.display_name, photo_id = result.photo_id, liker_name = result.liker_name, link= "/like/" + result.display_name + "/" + str(result.photo_id))
                list_of_digests.append(digest)
        elif photo.status_code == requests.codes.unavailable:
            raise HTTPException(status_code = 503, detail = "Mongo unavailable")
        elif photo.status_code == requests.codes.not_found:
            raise HTTPException(status_code = 404, detail = "Photo Not Found")
    except pymongo.errors.ServerSelectionTimeoutError:
        raise HTTPException(status_code=503, detail="Mongo unavailable")
    return {'items': list_of_digests}

@app.get("/like/{liker_name}", response_model = Likers, status_code = 200)
async def get_liker_all_photos(liker_name : str):
    logger.info("Get all the photos liked by a liker ...")

    list_of_digests = list()
    try:
        liker = requests.get(photographer_service + 'photographer/' + liker_name,
                                        timeout=REQUEST_TIMEOUT)
        # Make sure the liker exists
        if liker.status_code == requests.codes.ok: 
            async for result in Like.find(Like.liker_name == liker_name):
                digest = LikeDigest(display_name = result.display_name, photo_id = result.photo_id, liker_name = result.liker_name ,link= "/like/" + result.display_name + "/" + str(result.photo_id))
                list_of_digests.append(digest)
        elif liker.status_code == requests.codes.unavailable:
            raise HTTPException(status_code = 503, detail = "Mongo unavailable")
        elif photographer.status_code == requests.codes.not_found:
            raise HTTPException(status_code = 404, detail = "Photographer Not Found")
    except pymongo.errors.ServerSelectionTimeoutError:
        raise HTTPException(status_code=503, detail="Mongo unavailable")
    return {'items': list_of_digests}
    
@app.get("/like/{display_name}/{photo_id}/{liker_name}/information", status_code = 200)
async def get_like(display_name: str, photo_id: int, liker_name: str):
    logger.info("Get the detailed like information of a photo ...")
     
    try:
        photo = requests.get(f'{photo_service}/photo/{display_name}/{photo_id}',
                                        timeout=REQUEST_TIMEOUT)
        # Make sure the photo exists
        if photo.status_code == requests.codes.ok:
            like_info = await Like.find_one(Like.photo_id == photo_id, Like.display_name == display_name, Like.liker_name == liker_name)
            if like_info is not None:
                # return {"liker_name" : like_info.liker_name, "display_name" : like_info.display_name, "photo_id" : like_info.photo_id, "date" : like_info.date}
                return like_info
            else:
                raise HTTPException(status_code = 404, detail = "Like does not exist")
        elif photo.status_code == requests.codes.unavailable:
            raise HTTPException(status_code = 503, detail = "Mongo unavailable")
        elif photo.status_code == requests.codes.not_found:
            raise HTTPException(status_code = 404, detail = "Photo Not Found")
    except pymongo.errors.ServerSelectionTimeoutError:
        raise HTTPException(status_code=503, detail="Mongo unavailable")

@app.get("/like/{display_name}/{photo_id}/count", response_model = Count, status_code = 200)
async def count_like(display_name: str, photo_id: int):
    logger.info("Count the total amount of like of a photo ...")

    cnt = int()
    try:
        photo = requests.get(f'{photo_service}/photo/{display_name}/{photo_id}',
                                        timeout=REQUEST_TIMEOUT)
        # Make sure the photo exists
        if photo.status_code == requests.codes.ok:
            async for _ in Like.find(Like.photo_id == photo_id, Like.display_name == display_name):
                cnt += 1
        elif photo.status_code == requests.codes.unavailable:
            raise HTTPException(status_code = 503, detail = "Mongo unavailable")
        elif photo.status_code == requests.codes.not_found:
            raise HTTPException(status_code = 404, detail = "Photo Not Found")
    except pymongo.errors.ServerSelectionTimeoutError:
        raise HTTPException(status_code=503, detail="Mongo unavailable")
    return {'count': cnt}


@app.delete("/like/{display_name}/{photo_id}/{liker_name}", status_code = 200)
async def remove_like(display_name: str, photo_id: int, liker_name: str):
    logger.info("A liker removes a like to a photo ...")

    try:
        found =  await Like.find_one(Like.display_name == display_name, Like.photo_id == photo_id, Like.liker_name == liker_name)    
        if found:
            await found.delete()
        else:
            raise HTTPException(status_code = 503, detail = "Not Found")
    except pymongo.errors.ServerSelectionTimeoutError:
        raise HTTPException(status_code=503, detail="Mongo unavailable")

if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=80, log_level="info")
    # logger.setLevel(logging.DEBUG)
else:
    # logger.setLevel(gunicorn_logger.level)
    pass



    
