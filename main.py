from contextlib import asynccontextmanager

from fastapi import Depends, FastAPI, HTTPException, Query, status
from sqlalchemy.ext.asyncio import AsyncSession

import crud
from database import get_db, init_db
from schemas import (
    DishCreate,
    DishRead,
    DishUpdate,
    UserCreate,
    UserRead,
    UserUpdate,
)


@asynccontextmanager
async def lifespan(app: FastAPI):
    await init_db()
    yield


app = FastAPI(
    title="Async FastAPI: User + Dish",
    version="1.0.0",
    lifespan=lifespan,
)


@app.get("/", tags=["root"])
async def root():
    return {"message": "Async FastAPI is running 🚀"}


# ==================== USERS ====================
@app.post(
    "/users",
    response_model=UserRead,
    status_code=status.HTTP_201_CREATED,
    tags=["users"],
)
async def create_user(payload: UserCreate, db: AsyncSession = Depends(get_db)):
    if await crud.get_user_by_name(db, payload.name):
        raise HTTPException(status_code=400, detail="User with this name already exists")
    return await crud.create_user(db, payload)


@app.get("/users", response_model=list[UserRead], tags=["users"])
async def list_users(
    skip: int = 0,
    limit: int = Query(100, le=500),
    db: AsyncSession = Depends(get_db),
):
    return await crud.get_users(db, skip=skip, limit=limit)


@app.get("/users/{user_id}", response_model=UserRead, tags=["users"])
async def get_user(user_id: int, db: AsyncSession = Depends(get_db)):
    user = await crud.get_user(db, user_id)
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    return user


@app.patch("/users/{user_id}", response_model=UserRead, tags=["users"])
async def update_user(
    user_id: int, payload: UserUpdate, db: AsyncSession = Depends(get_db)
):
    user = await crud.get_user(db, user_id)
    if not user:
        raise HTTPException(status_code=404, detail="User not found")

    # проверка уникальности нового имени
    if payload.name and payload.name != user.name:
        existing = await crud.get_user_by_name(db, payload.name)
        if existing:
            raise HTTPException(status_code=400, detail="Name already taken")

    return await crud.update_user(db, user, payload)


@app.delete(
    "/users/{user_id}", status_code=status.HTTP_204_NO_CONTENT, tags=["users"]
)
async def delete_user(user_id: int, db: AsyncSession = Depends(get_db)):
    user = await crud.get_user(db, user_id)
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    await crud.delete_user(db, user)


# ==================== DISHES ====================
@app.post(
    "/dishes",
    response_model=DishRead,
    status_code=status.HTTP_201_CREATED,
    tags=["dishes"],
)
async def create_dish(payload: DishCreate, db: AsyncSession = Depends(get_db)):
    return await crud.create_dish(db, payload)


@app.get("/dishes", response_model=list[DishRead], tags=["dishes"])
async def list_dishes(
    skip: int = 0,
    limit: int = Query(100, le=500),
    category: str | None = Query(None, description="Фильтр по категории"),
    search: str | None = Query(None, description="Поиск по названию"),
    db: AsyncSession = Depends(get_db),
):
    return await crud.get_dishes(
        db, skip=skip, limit=limit, category=category, search=search
    )


@app.get("/dishes/{dish_id}", response_model=DishRead, tags=["dishes"])
async def get_dish(dish_id: int, db: AsyncSession = Depends(get_db)):
    dish = await crud.get_dish(db, dish_id)
    if not dish:
        raise HTTPException(status_code=404, detail="Dish not found")
    return dish


@app.patch("/dishes/{dish_id}", response_model=DishRead, tags=["dishes"])
async def update_dish(
    dish_id: int, payload: DishUpdate, db: AsyncSession = Depends(get_db)
):
    dish = await crud.get_dish(db, dish_id)
    if not dish:
        raise HTTPException(status_code=404, detail="Dish not found")
    return await crud.update_dish(db, dish, payload)


@app.delete(
    "/dishes/{dish_id}", status_code=status.HTTP_204_NO_CONTENT, tags=["dishes"]
)
async def delete_dish(dish_id: int, db: AsyncSession = Depends(get_db)):
    dish = await crud.get_dish(db, dish_id)
    if not dish:
        raise HTTPException(status_code=404, detail="Dish not found")
    await crud.delete_dish(db, dish)