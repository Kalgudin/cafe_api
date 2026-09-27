from fastapi import FastAPI

from main_base import *

app = FastAPI()
@app.get("/")
async def home() -> dict:
    return {"data": "message"}
@app.get("/menu")
async def menu() -> dict:
    return {"menu": 'cofe'}

@app.get("/users")
async def users() -> dict:
    Session = sessionmaker(bind=engine)
    session = Session()
    users = session.query(User).all()
    session.close()
    res = {}

    for user in users:
        res[f'{user.id}'] = {'name':f'{user.name}', 'passward':f'{user.password}'}
    return res
