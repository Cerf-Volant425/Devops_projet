from mongoengine import *

class Photo(Document):
    display_name = StringField(max_length=120, required=True)
    image_file = ImageField(required=True, size=(800, 600, True))
    photo_id = IntField(required=True)
    author = StringField(max_length=120, required=False)
    title = StringField(max_length=100, required=False)
    comment = StringField(max_length=100, required=False)
    location = StringField(max_length=100, required=False)
    tags = ListField(StringField(max_length=30), required=False)
