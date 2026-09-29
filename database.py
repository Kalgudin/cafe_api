from sqlalchemy.ext.asyncio import create_async_engine, async_sessionmaker, AsyncSession
from sqlalchemy.orm import DeclarativeBase

# строка подключения к postgres
# DATABASE_URL = "postgresql+asyncpg://postgres:Xzxz0011@localhost:5432/coffee_db"
DATABASE_URL = "sqlite+aiosqlite:///./app.db"

engine = create_async_engine(DATABASE_URL)

# фабрика сессий
SessionLocal = async_sessionmaker(engine, class_=AsyncSession, expire_on_commit=False)


# базовый класс для моделей
class Base(DeclarativeBase):
    pass


# зависимость для эндпоинтов
async def get_db():
    async with SessionLocal() as session:
        yield session