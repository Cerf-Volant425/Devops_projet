#!/usr/bin/env python3

from pydantic import BaseModel
from typing import List

REQUEST_TIMEOUT = 5

class PhotoAttributesNoTags(BaseModel):
    title: str
    comment: str
    location: str
    author: str

class PhotoAttributes(PhotoAttributesNoTags):
    tags: List[str]

class PhotoDigest(BaseModel):
    photo_id: int
    link: str

class Photos(BaseModel):
    items: List[PhotoDigest]
    has_more: bool
