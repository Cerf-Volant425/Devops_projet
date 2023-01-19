#!/usr/bin/env python3

import logging
import json

from photo import Photo
from photoId import PhotoId

from mongoengine import *
import socket
import pymongo

from bson.objectid import ObjectId
from bson import json_util
from bson.errors import InvalidId

#from flask import jsonify
import json
#import flask
import robustify

@robustify.retry_mongo
def mongo_save_photo(upfile, display_name, photo_id):
    try:
        photo = Photo(image_file=upfile, photo_id=photo_id, display_name=display_name,
                      comment="unset",
                      author="unset",
                      title="unset",
                      location="unset",
                      tags=[])
        photo.save()
    except (IOError):
        return False
    except (pymongo.errors.AutoReconnect,
            pymongo.errors.ServerSelectionTimeoutError,
            pymongo.errors.NetworkTimeout) as e:
        raise 
    return True

@robustify.retry_mongo
def mongo_allocate_photo_id(display_name):
    try:
        ph_id = PhotoId.objects(display_name=display_name).get()
        photo_id = ph_id.next_photo_id
        ph_id.next_photo_id += 1
        ph_id.save()
        return photo_id
    except PhotoId.DoesNotExist as e:
        ph_id = PhotoId(display_name=display_name, next_photo_id=1).save()
        return 0

@robustify.retry_mongo
def mongo_get_photo_by_name_and_id(display_name, photo_id):
    try:
        ph = Photo.objects(photo_id=photo_id, display_name=display_name).get()
        return ph
    except (pymongo.errors.AutoReconnect,
            pymongo.errors.ServerSelectionTimeoutError,
            pymongo.errors.NetworkTimeout) as e:
        raise 

@robustify.retry_mongo
def mongo_delete_photo_by_name_and_id(display_name, photo_id):
    try:
        ph = Photo.objects(photo_id=photo_id, display_name=display_name).get()
    except (pymongo.errors.AutoReconnect,
            pymongo.errors.ServerSelectionTimeoutError,
            pymongo.errors.NetworkTimeout) as e:
        raise 
    except (Photo.DoesNotExist) as e:
        return False
    ph.delete()
    return True

@robustify.retry_mongo
def mongo_get_photos_by_name(display_name, offset, limit):
    try:
        qs = Photo.objects(display_name=display_name).order_by('photo_id').skip(offset).limit(limit)
        if qs.count(with_limit_and_skip = False) > (offset + limit):
            has_more = True
        else:
            has_more = False
    except (pymongo.errors.AutoReconnect,
            pymongo.errors.ServerSelectionTimeoutError,
            pymongo.errors.NetworkTimeout) as e:
        raise 
    return (has_more, qs)

@robustify.retry_mongo
def mongo_set_photo_attributes(display_name, photo_id, attributes, photo_all_attributes):
    try:
        qs = Photo.objects(photo_id=photo_id, display_name=display_name)
        for key, value in attributes.items():
            set_attr = "set__" + key 
            qs.update (**{set_attr: value})

        for element in photo_all_attributes:
            if not element in attributes:
                set_attr = "set__" + element 
                qs.update (**{set_attr: "--unset--"})
        return qs
    except (pymongo.errors.AutoReconnect,
            pymongo.errors.ServerSelectionTimeoutError,
            pymongo.errors.NetworkTimeout) as e:
        raise
