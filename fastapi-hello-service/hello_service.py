#!/usr/bin/env python3

import uvicorn

from fastapi import FastAPI, HTTPException
from fastapi import Path

app = FastAPI()

@app.get("/hello", status_code=200)
def say_hello():
    return {'message': 'hello'}

@app.get("/hello/{firstname}", status_code=200)
def test(firstname, level): 
    
    if level == 'familiar':
        mes = "hello,"+firstname
    elif level == "formal" :
        mes = "nice to meet you " +firstname
    else :
        mes = "nice to see you ,  " + firstname

    return {'message': mes }


if __name__ == "__main__":
    uvicorn.run(app, log_level="info")

