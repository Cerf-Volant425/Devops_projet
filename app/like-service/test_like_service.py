import pytest
# from starlette.testclient import TestClient
import json
from bson import json_util
import logging
import unittest.mock
# from fastapi.testclient import TestClient
from like_service import app
from beanie import Document, init_beanie
from httpx import AsyncClient, Request
from like_service import *
#logging.basicConfig(level=logging.DEBUG)


data1 = {
         'liker_name': 'nmsl',
         'date': '25-04-2000'
        }

data2 = {
         'liker_name': 'nmhl',
         'date': '09-05-2000'
        }

headers_content = {'Content-Type': 'application/json'}
headers_accept  = {'Accept': 'application/json'}



@pytest.mark.asyncio
@unittest.mock.patch('like_service.requests.get')
@pytest.mark.usefixtures("clearLikers")
@pytest.mark.usefixtures("initDB")


async def test_give_like_once(requests_get):

    requests_get.return_value.status_code = 200
    async with AsyncClient(app=app, base_url="http://test") as ac:
    
        response = await ac.post('/like/timo/0',
                                headers=headers_content,
                                content=json.dumps(data1))
        #print(response)
        assert response.headers['Location']
        assert response.status_code == 201

@pytest.mark.asyncio
@unittest.mock.patch('like_service.requests.get')
@pytest.mark.usefixtures("clearLikers")
@pytest.mark.usefixtures("initDB")

async def test_give_like_twice(requests_get):

    requests_get.return_value.status_code = 200
    async with AsyncClient(app=app, base_url="http://test") as ac:
        response1 = await ac.post('/like/timo/0',
                                  headers=headers_content,
                                  content=json.dumps(data1))
        assert response1.status_code == 201

        response2 = await ac.post('/like/timo/0',
                                  headers=headers_content,
                                  content=json.dumps(data1))
        assert response2.status_code == 409

@pytest.mark.asyncio
@unittest.mock.patch('like_service.requests.get')
@pytest.mark.usefixtures("clearLikers")
@pytest.mark.usefixtures("initDB")

async def test_get_like(requests_get):

    requests_get.return_value.status_code = 200
    async with AsyncClient(app=app, base_url="http://test") as ac:
        response = await ac.post('/like/timo/0',
                           headers=headers_content,
                           content=json.dumps(data1))
        assert response.headers['Location']
        assert response.status_code == 201

        response2 = await ac.get('/like/timo/0')
        assert response2.status_code == 200

@pytest.mark.asyncio
@unittest.mock.patch('like_service.requests.get')
@pytest.mark.usefixtures("clearLikers")
@pytest.mark.usefixtures("initDB")

async def test_get_photo_all_likers(requests_get):

    requests_get.return_value.status_code = 200
    async with AsyncClient(app=app, base_url="http://test") as ac:
        response1 = await ac.post('/like/timo/0',
                           headers=headers_content,
                           content=json.dumps(data1))
        assert response1.headers['Location']
        assert response1.status_code == 201

        response2 = await ac.post('/like/timo/0',
                           headers=headers_content,
                           content=json.dumps(data2))
        assert response2.headers['Location']
        assert response2.status_code == 201

        response3 = await ac.get('/like/timo/0')
        assert response3.status_code == 200

@pytest.mark.asyncio
@unittest.mock.patch('like_service.requests.get')
@pytest.mark.usefixtures("clearLikers")
@pytest.mark.usefixtures("initDB")

async def test_get_liker_all_photos(requests_get):

    requests_get.return_value.status_code = 200
    async with AsyncClient(app=app, base_url="http://test") as ac:
        response1 = await ac.post('/like/timo/0',
                           headers=headers_content,
                           content=json.dumps(data1))
        assert response1.headers['Location']
        assert response1.status_code == 201

        response2 = await ac.post('/like/timo/1',
                           headers=headers_content,
                           content=json.dumps(data2))
        assert response2.headers['Location']
        assert response2.status_code == 201

        response3 = await ac.get('/like/timo')
        assert response3.status_code == 200

@pytest.mark.asyncio
@unittest.mock.patch('like_service.requests.get')
@pytest.mark.usefixtures("clearLikers")
@pytest.mark.usefixtures("initDB")

async def test_has_delete_likes(requests_get):

    requests_get.return_value.status_code = 200
    async with AsyncClient(app=app, base_url="http://test") as ac:
        response1 = await ac.post('/like/timo/0',
                                headers=headers_content,
                                content=json.dumps(data1))
                   
        assert response1.headers['Location']
        assert response1.status_code == 201
 
        response2=await ac.delete(url='/like/timo/0/nmsl')
        assert response2.status_code == 200
        
@pytest.mark.asyncio
@unittest.mock.patch('like_service.requests.get')
@pytest.mark.usefixtures("clearLikers")
@pytest.mark.usefixtures("initDB")

async def test_count_like(requests_get):

    requests_get.return_value.status_code = 200
    async with AsyncClient(app=app, base_url="http://test") as ac:
        response1 = await ac.post('/like/timo/0',
                                headers=headers_content,
                                content=json.dumps(data1))
        assert response1.headers['Location']
        assert response1.status_code == 201
        
        response2 = await ac.post('/like/timo/0',
                           headers=headers_content,
                           content=json.dumps(data2))
        assert response2.headers['Location']
        assert response2.status_code == 201

        response3 = await ac.get('/like/timo/0/count')
        assert response3.status_code == 200


