from sqlalchemy import create_engine
from sqlalchemy.orm import declarative_base, sessionmaker
from sqlalchemy import Column, Integer, String



# engine = create_engine('postgresql+psycopg2://user:password@localhost/dbname')
engine = create_engine('sqlite:///cafe_base.db')
Base = declarative_base()
Base.metadata.create_all(engine)

class User(Base):
    __tablename__ = 'users'
    id = Column(Integer, primary_key=True)
    name = Column(String(50), unique=True, nullable=False)
    password = Column(String, nullable=False)

    def __init__(self, name, password):
        self.name = name
        self.password = password


class Dish(Base):
    __tablename__ = 'dishes' # множественное число
    id = Column(Integer, primary_key=True)
    name = Column(String(50), unique=True, nullable=False)
    category = Column(String(50), nullable=False)
    price = Column(Integer, nullable=False)
    description = Column(String, nullable=False)
    foto = Column(String, nullable=False)

    def __init__(self, name, category, price, description, foto):
        self.name = name
        self.category = category
        self.price = price
        self.description = description
        self.foto = foto

from pydantic import BaseModel

class DishCreate(BaseModel): # используется для внесения данных в базу
    name = str
    category = str
    price = int
    description = str
    foto = str


async def add_user(name, password):
    Session = sessionmaker(bind=engine)
    session = Session()
    user = User(name=name, password=password)
    session.add(user)

    try:
        # Подтверждаем транзакцию
        session.commit()
        print("Пользователь успешно добавлен!")
    except:
        # В случае ошибки откатываем транзакцию
        session.rollback()
        print("Произошла ошибка, откатываем транзакцию.")
    finally:
        # Закрываем сессию
        session.close()

async def get_all_users():
    Session = sessionmaker(bind=engine)
    session = Session()
    users = session.query(User).all()
    session.close()
    li = {}
    for user in users:
        li.update({f'{user.name}': f'{user.password}'})
    print(li)
    return li



