import pytest

from mongoengine import connect

from photo import Photo
from photoId import PhotoId

@pytest.fixture
def clearPhotos():
    Photo.objects.all().delete()
    PhotoId.objects.all().delete()

@pytest.fixture(scope="class")
def initDB():
    connect("photos", alias="default", host="mongo-service-test")
    yield
