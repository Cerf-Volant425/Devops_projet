#!/usr/bin/env python3

from fastapi import Path, Body
from pydantic import BaseModel, Field
from typing import List
from beanie import Document, init_beanie

class Lname:
    STR = "The name of the liker"
    MAX_LENGTH = 16
    PATH_PARAM = Path(..., title = STR, max_length = MAX_LENGTH)

class Dname:
    STR = "The display name of the photographer"
    MAX_LENGTH = 16
    PATH_PARAM = Path(..., title = STR, max_length = MAX_LENGTH)

class Pid:
    STR = 'The id of the liked photo' 

class Date:
    STR = 'The date of the like operation'
    MAX_LENGTH = 16

class LikeDesc(BaseModel):
    liker_name: str = Field (None, title = Lname.STR, max_length = Lname.MAX_LENGTH)
    display_name: str = Field (None, title = Dname.STR, max_length = Dname.MAX_LENGTH)
    photo_id: int = Field (None, title = Pid.STR)
    date: str = Field (None, title = Date.STR, max_length = Date.MAX_LENGTH)

class Like(Document, LikeDesc):
    pass

LIKE_EXAMPLE = {
    "liker_name": "rdoisneau",
    # "photo_id": "0",
    "date": "25/04/2000"
    }

LIKE_BODY = Body(..., example = LIKE_EXAMPLE)

class LikeDigest(BaseModel):
    liker_name: str
    display_name: str
    photo_id: int
    link: str
    

class Likers(BaseModel):
    items: List[LikeDigest]
    
class Count(BaseModel):
    count: int
