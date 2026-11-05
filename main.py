import asyncio
import sys

# ЭТИ ДВЕ СТРОКИ ОБЯЗАТЕЛЬНЫ ДЛЯ WINDOWS + ASYNCPG
if sys.platform == "win32":
    asyncio.set_event_loop_policy(asyncio.WindowsSelectorEventLoopPolicy())

# Только теперь импорты
from fastapi import FastAPI, Depends, HTTPException
from sqlalchemy import select
from sqlalchemy.orm import selectinload
from sqlalchemy.ext.asyncio import AsyncSession

from database import Base, engine, get_db
from models import (
    User, UserCreate, UserOut, LoginData, hash_password,
    MenuItem, MenuItemCreate, MenuItemOut,
    Order, OrderCreate, OrderOut, OrderFull,
    OrderItem,
    Favorite, FavoriteCreate, FavoriteOut,
    Promotion, PromotionCreate, PromotionOut,
    LoyaltyTransaction, LoyaltyCreate, LoyaltyOut,
)

app = FastAPI(title="Coffee API")


@app.on_event("startup")
async def on_startup():
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    print("База готова")


# ==================== USERS ====================
@app.post("/users", response_model=UserOut)
async def create_user(data: UserCreate, db: AsyncSession = Depends(get_db)):
    exists = await db.execute(select(User).where(User.phone == data.phone))
    if exists.scalar_one_or_none():
        raise HTTPException(400, "Такой телефон уже зарегистрирован")

    new_user = User(
        name=data.name,
        phone=data.phone,
        password_hash=hash_password(data.password),
    )
    db.add(new_user)
    await db.commit()
    await db.refresh(new_user)
    return new_user


@app.post("/login", response_model=UserOut)
async def login(data: LoginData, db: AsyncSession = Depends(get_db)):
    result = await db.execute(select(User).where(User.phone == data.phone))
    found_user = result.scalar_one_or_none()
    if not found_user:
        raise HTTPException(401, "Неверный телефон или пароль")

    if found_user.password_hash != hash_password(data.password):
        raise HTTPException(401, "Неверный телефон или пароль")

    return found_user


@app.get("/users", response_model=list[UserOut])
async def get_users(db: AsyncSession = Depends(get_db)):
    result = await db.execute(select(User))
    return result.scalars().all()


@app.get("/users/{user_id}", response_model=UserOut)
async def get_user(user_id: int, db: AsyncSession = Depends(get_db)):
    found = await db.get(User, user_id)
    if not found:
        raise HTTPException(404, "Пользователь не найден")
    return found


@app.delete("/users/{user_id}")
async def delete_user(user_id: int, db: AsyncSession = Depends(get_db)):
    found = await db.get(User, user_id)
    if not found:
        raise HTTPException(404, "Пользователь не найден")
    await db.delete(found)
    await db.commit()
    return {"ok": True}


# ==================== MENU ====================
@app.post("/menu", response_model=MenuItemOut)
async def create_menu(data: MenuItemCreate, db: AsyncSession = Depends(get_db)):
    new_item = MenuItem(**data.model_dump())
    db.add(new_item)
    await db.commit()
    await db.refresh(new_item)
    return new_item


@app.get("/menu", response_model=list[MenuItemOut])
async def get_menu(db: AsyncSession = Depends(get_db)):
    result = await db.execute(select(MenuItem))
    return result.scalars().all()


@app.get("/menu/{item_id}", response_model=MenuItemOut)
async def get_menu_item(item_id: int, db: AsyncSession = Depends(get_db)):
    found = await db.get(MenuItem, item_id)
    if not found:
        raise HTTPException(404, "Позиция не найдена")
    return found


@app.delete("/menu/{item_id}")
async def delete_menu_item(item_id: int, db: AsyncSession = Depends(get_db)):
    found = await db.get(MenuItem, item_id)
    if not found:
        raise HTTPException(404, "Позиция не найдена")
    await db.delete(found)
    await db.commit()
    return {"ok": True}


# ==================== ORDERS ====================
@app.post("/orders", response_model=OrderOut)
async def create_order(data: OrderCreate, db: AsyncSession = Depends(get_db)):
    # 1) проверяем пользователя
    found_user = await db.get(User, data.user_id)
    if not found_user:
        raise HTTPException(404, "Пользователь не найден")

    # 2) создаём заказ (переменная НАЗЫВАЕТСЯ new_order, чтобы не затереть ничего встроенного)
    new_order = Order(user_id=data.user_id, delivery_method=data.delivery_method, total=0)
    db.add(new_order)
    await db.flush()   # получаем new_order.id

    # 3) создаём позиции
    total = 0
    for item in data.items:
        found_menu_item = await db.get(MenuItem, item.menu_item_id)
        if not found_menu_item:
            raise HTTPException(404, f"Позиция {item.menu_item_id} не найдена")
        if not found_menu_item.is_available:
            raise HTTPException(400, f"{found_menu_item.name} недоступна")

        price = float(found_menu_item.price) * item.quantity
        total += price

        db.add(OrderItem(
            order_id=new_order.id,
            menu_item_id=item.menu_item_id,
            quantity=item.quantity,
            drink_options=item.drink_options,
            price=price,
        ))

    # 4) сохраняем сумму
    new_order.total = total
    await db.commit()
    await db.refresh(new_order)
    return new_order


@app.get("/orders", response_model=list[OrderFull])
async def get_orders(db: AsyncSession = Depends(get_db)):
    result = await db.execute(
        select(Order).options(selectinload(Order.items))
    )
    return result.scalars().all()


@app.get("/orders/{order_id}", response_model=OrderOut)
async def get_order(order_id: int, db: AsyncSession = Depends(get_db)):
    found = await db.get(Order, order_id)
    if not found:
        raise HTTPException(404, "Заказ не найден")
    return found


@app.patch("/orders/{order_id}/status")
async def update_status(order_id: int, status: str, db: AsyncSession = Depends(get_db)):
    found = await db.get(Order, order_id)
    if not found:
        raise HTTPException(404, "Заказ не найден")
    found.status = status
    await db.commit()
    return {"ok": True}


@app.delete("/orders/{order_id}")
async def delete_order(order_id: int, db: AsyncSession = Depends(get_db)):
    found = await db.get(Order, order_id)
    if not found:
        raise HTTPException(404, "Заказ не найден")
    await db.delete(found)
    await db.commit()
    return {"ok": True}


# ==================== FAVORITES ====================
@app.post("/favorites", response_model=FavoriteOut)
async def add_favorite(data: FavoriteCreate, db: AsyncSession = Depends(get_db)):
    new_fav = Favorite(**data.model_dump())
    db.add(new_fav)
    await db.commit()
    await db.refresh(new_fav)
    return new_fav


@app.get("/favorites/{user_id}", response_model=list[FavoriteOut])
async def get_favorites(user_id: int, db: AsyncSession = Depends(get_db)):
    result = await db.execute(select(Favorite).where(Favorite.user_id == user_id))
    return result.scalars().all()


@app.delete("/favorites/{fav_id}")
async def delete_favorite(fav_id: int, db: AsyncSession = Depends(get_db)):
    found = await db.get(Favorite, fav_id)
    if not found:
        raise HTTPException(404, "Избранное не найдено")
    await db.delete(found)
    await db.commit()
    return {"ok": True}


# ==================== PROMOTIONS ====================
@app.post("/promotions", response_model=PromotionOut)
async def create_promotion(data: PromotionCreate, db: AsyncSession = Depends(get_db)):
    new_promo = Promotion(**data.model_dump())
    db.add(new_promo)
    await db.commit()
    await db.refresh(new_promo)
    return new_promo


@app.get("/promotions/{user_id}", response_model=list[PromotionOut])
async def get_promotions(user_id: int, db: AsyncSession = Depends(get_db)):
    result = await db.execute(select(Promotion).where(Promotion.user_id == user_id))
    return result.scalars().all()


@app.delete("/promotions/{promo_id}")
async def delete_promotion(promo_id: int, db: AsyncSession = Depends(get_db)):
    found = await db.get(Promotion, promo_id)
    if not found:
        raise HTTPException(404, "Акция не найдена")
    await db.delete(found)
    await db.commit()
    return {"ok": True}


# ==================== LOYALTY ====================
@app.post("/loyalty", response_model=LoyaltyOut)
async def create_loyalty(data: LoyaltyCreate, db: AsyncSession = Depends(get_db)):
    found_user = await db.get(User, data.user_id)
    if not found_user:
        raise HTTPException(404, "Пользователь не найден")

    if data.operation_type == "accrual":
        found_user.balance_points += data.points
    elif data.operation_type == "spend":
        if found_user.balance_points < data.points:
            raise HTTPException(400, "Недостаточно баллов")
        found_user.balance_points -= data.points
    elif data.operation_type == "refund":
        found_user.balance_points += data.points
    else:
        raise HTTPException(400, "Тип операции: accrual / spend / refund")

    new_tx = LoyaltyTransaction(**data.model_dump())
    db.add(new_tx)
    await db.commit()
    await db.refresh(new_tx)
    return new_tx


@app.get("/loyalty/{user_id}", response_model=list[LoyaltyOut])
async def get_loyalty(user_id: int, db: AsyncSession = Depends(get_db)):
    result = await db.execute(
        select(LoyaltyTransaction).where(LoyaltyTransaction.user_id == user_id)
    )
    return result.scalars().all()
@app.get("/health"), async def health_check(), return {«status»: «ok»}
