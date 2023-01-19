from mongoengine import *

class PhotoId(Document):
    display_name = StringField(max_length=120, required=True)
    next_photo_id = IntField(required=True)
