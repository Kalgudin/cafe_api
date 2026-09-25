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
async def users() -> list:
    Session = sessionmaker(bind=engine)
    session = Session()
    users = session.query(User).all()
    session.close()
    li = []

    for user in users:
        li.update({'name':f'{user.name}', 'passward':f'{user.password}'})
    print(li)
    return li
