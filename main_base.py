from sqlalchemy import create_engine
from sqlalchemy.orm import declarative_base, sessionmaker
from sqlalchemy import Column, Integer, String



# engine = create_engine('postgresql+psycopg2://user:password@localhost/dbname')
engine = create_engine('sqlite:///cafe_base.db')
Base = declarative_base()


class User(Base):
    __tablename__ = 'users'
    id = Column(Integer, primary_key=True)
    name = Column(String(50), unique=True, nullable=False)
    password = Column(String, nullable=False)

    def __init__(self, name, password):
        self.name = name
        self.password = password


Base.metadata.create_all(engine)

def add_user(name, password):
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

def get_all_users():
    Session = sessionmaker(bind=engine)
    session = Session()
    users = session.query(User).all()
    session.close()
    li = {}
    print(li)
    for user in users:
        li.update({f'{user.name}': f'{user.password}'})
    print(li)
    return li



