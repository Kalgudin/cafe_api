from fastapi import FastAPI, Body
from sqlalchemy.ext.asyncio import create_async_engine, async_sessionmaker, AsyncSession
from sqlalchemy.orm import declarative_base, sessionmaker

from main_base import DishCreate, Dish, User

engine = create_async_engine('sqlite:///cafe_base.db')
Base = declarative_base()
Base.metadata.create_all(engine)

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
@app.get("/dishes/{category}")
async def dishes(category: str) -> dict:
    Session = sessionmaker(bind=engine)
    session = Session()
    try: dishes = session.query(Dish).filter(Dish.category == category).all()
    except: dishes = session.query(Dish).all()

    session.close()
    res = {}

    for dish in dishes:
        res[f'{dish.id}'] = {'name':f'{dish.name}',
                             'description':f'{dish.description}',
                             'price':f'{str(dish.price)}',
                             'foto':f'{dish.foto}'}
    return res


@app.post("/add_dishes")
async def add_dish(dish_data: DishCreate = Body(...)):
    Session = async_sessionmaker(bind=engine)
    session = Session()
    new_dish = Dish(name=dish_data.name, description=dish_data.description, price=dish_data.price)
    session.add(new_dish)

    try:
        # Подтверждаем транзакцию
        session.commit()
        print("Блюдо успешно добавлено!")
    except:
        # В случае ошибки откатываем транзакцию
        session.rollback()
        print("Произошла ошибка, откатываем транзакцию.")
    finally:
        # Закрываем сессию
        session.close()



