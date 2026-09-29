from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker, create_async_engine
from sqlalchemy.orm import DeclarativeBase

DATABASE_URL = "sqlite+aiosqlite:///./app.db"

engine = create_async_engine(DATABASE_URL, echo=False, future=True)

AsyncSessionLocal = async_sessionmaker(
    bind=engine,
    class_=AsyncSession,
    expire_on_commit=False,
    autoflush=False,
)


class Base(DeclarativeBase):
    pass


async def get_db() -> AsyncSession:
    """Dependency для получения асинхронной сессии."""
    async with AsyncSessionLocal() as session:
        yield session


async def init_db() -> None:
    """Создание таблиц при старте приложения."""
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)