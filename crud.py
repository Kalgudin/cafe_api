from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from models import Dish, User
from schemas import DishCreate, DishUpdate, UserCreate, UserUpdate


# ==================== USERS ====================
async def get_users(db: AsyncSession, skip: int = 0, limit: int = 100) -> list[User]:
    result = await db.execute(select(User).offset(skip).limit(limit))
    return list(result.scalars().all())


async def get_user(db: AsyncSession, user_id: int) -> User | None:
    return await db.get(User, user_id)


async def get_user_by_name(db: AsyncSession, name: str) -> User | None:
    result = await db.execute(select(User).where(User.name == name))
    return result.scalar_one_or_none()


async def create_user(db: AsyncSession, data: UserCreate) -> User:
    user = User(**data.model_dump())
    db.add(user)
    await db.commit()
    await db.refresh(user)
    return user


async def update_user(db: AsyncSession, user: User, data: UserUpdate) -> User:
    for field, value in data.model_dump(exclude_unset=True).items():
        setattr(user, field, value)
    await db.commit()
    await db.refresh(user)
    return user


async def delete_user(db: AsyncSession, user: User) -> None:
    await db.delete(user)
    await db.commit()


# ==================== DISHES ====================
async def get_dishes(
    db: AsyncSession,
    skip: int = 0,
    limit: int = 100,
    category: str | None = None,
    search: str | None = None,
) -> list[Dish]:
    stmt = select(Dish)
    if category:
        stmt = stmt.where(Dish.category == category)
    if search:
        stmt = stmt.where(Dish.name.ilike(f"%{search}%"))
    stmt = stmt.offset(skip).limit(limit)
    result = await db.execute(stmt)
    return list(result.scalars().all())


async def get_dish(db: AsyncSession, dish_id: int) -> Dish | None:
    return await db.get(Dish, dish_id)


async def create_dish(db: AsyncSession, data: DishCreate) -> Dish:
    dish = Dish(**data.model_dump())
    db.add(dish)
    await db.commit()
    await db.refresh(dish)
    return dish


async def update_dish(db: AsyncSession, dish: Dish, data: DishUpdate) -> Dish:
    for field, value in data.model_dump(exclude_unset=True).items():
        setattr(dish, field, value)
    await db.commit()
    await db.refresh(dish)
    return dish


async def delete_dish(db: AsyncSession, dish: Dish) -> None:
    await db.delete(dish)
    await db.commit()