# import asyncio
# import sys

# # фикс asyncpg на Windows
# if sys.platform == "win32":
#     asyncio.set_event_loop_policy(asyncio.WindowsSelectorEventLoopPolicy())

from fastapi import FastAPI, Depends, HTTPException
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from database import Base, engine, get_db
from models import * #User, MenuItem, Order, OrderItem, Favorite, Promotion, LoyaltyTransaction
app = FastAPI(title="Coffee API")


@app.on_event("startup")
async def on_startup():
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    print("База готова")

@app.get("/", tags=["root"])
async def root():
    return {"message": "Заработало!!!"}

# ==================== USERS ====================
@app.post("/users", response_model=UserOut)
async def create_user(data: UserCreate, db: AsyncSession = Depends(get_db)):
    # проверяем, что телефон свободен
    exists = await db.execute(select(User).where(User.phone == data.phone))
    if exists.scalar_one_or_none():
        raise HTTPException(400, "Такой телефон уже зарегистрирован")

    # вручную, а не User(**data.model_dump()) — потому что password нужно хешировать
    user = User(
        name=data.name,
        phone=data.phone,
        password_hash=hash_password(data.password),
    )
    db.add(user)
    await db.commit()
    await db.refresh(user)
    return user

@app.post("/login", response_model=UserOut)
async def login(data: LoginData, db: AsyncSession = Depends(get_db)):
    result = await db.execute(select(User).where(User.phone == data.phone))
    user = result.scalar_one_or_none()
    if not user:
        raise HTTPException(401, "Неверный телефон или пароль")

    if user.password_hash != hash_password(data.password):
        raise HTTPException(401, "Неверный телефон или пароль")

    return user


@app.get("/users", response_model=list[UserOut])
async def get_users(db: AsyncSession = Depends(get_db)):
    result = await db.execute(select(User))
    return result.scalars().all()


@app.get("/users/{user_id}", response_model=UserOut)
async def get_user(user_id: int, db: AsyncSession = Depends(get_db)):
    user = await db.get(User, user_id)
    if not user:
        raise HTTPException(404, "Пользователь не найден")
    return user


@app.delete("/users/{user_id}")
async def delete_user(user_id: int, db: AsyncSession = Depends(get_db)):
    user = await db.get(User, user_id)
    if not user:
        raise HTTPException(404, "Пользователь не найден")
    await db.delete(user)
    await db.commit()
    return {"ok": True}


# ==================== MENU ====================
@app.post("/menu", response_model=MenuItemOut)
async def create_menu(data: MenuItemCreate, db: AsyncSession = Depends(get_db)):
    item = MenuItem(**data.model_dump())
    db.add(item)
    await db.commit()
    await db.refresh(item)
    return item


@app.get("/menu", response_model=list[MenuItemOut])
async def get_menu(db: AsyncSession = Depends(get_db)):
    result = await db.execute(select(MenuItem))
    return result.scalars().all()


@app.get("/menu/{item_id}", response_model=MenuItemOut)
async def get_menu_item(item_id: int, db: AsyncSession = Depends(get_db)):
    item = await db.get(MenuItem, item_id)
    if not item:
        raise HTTPException(404, "Позиция не найдена")
    return item


@app.delete("/menu/{item_id}")
async def delete_menu_item(item_id: int, db: AsyncSession = Depends(get_db)):
    item = await db.get(MenuItem, item_id)
    if not item:
        raise HTTPException(404, "Позиция не найдена")
    await db.delete(item)
    await db.commit()
    return {"ok": True}


# ==================== ORDERS ====================
@app.post("/orders", response_model=OrderOut)
async def create_order(data: OrderCreate, db: AsyncSession = Depends(get_db)):
    user = await db.get(User, data.user_id)
    if not user:
        raise HTTPException(404, "Пользователь не найден")

    order = Order(user_id=data.user_id, delivery_method=data.delivery_method, total=0)
    db.add(order)
    await db.flush()

    total = 0
    for item in data.items:
        menu_item = await db.get(MenuItem, item.menu_item_id)
        if not menu_item:
            raise HTTPException(404, f"Позиция {item.menu_item_id} не найдена")
        if not menu_item.is_available:
            raise HTTPException(400, f"{menu_item.name} недоступна")

        price = float(menu_item.price) * item.quantity
        total += price

        order.items.append(OrderItem(
            menu_item_id=item.menu_item_id,
            quantity=item.quantity,
            drink_options=item.drink_options,
            price=price,
        ))

    order.total = total
    await db.commit()
    await db.refresh(order)
    return order


@app.get("/orders", response_model=list[OrderFull])
async def get_orders(db: AsyncSession = Depends(get_db)):
    result = await db.execute(
        select(Order).options(selectinload(Order.items))
    )
    return result.scalars().all()


@app.get("/orders/{order_id}", response_model=OrderOut)
async def get_order(order_id: int, db: AsyncSession = Depends(get_db)):
    order = await db.get(Order, order_id)
    if not order:
        raise HTTPException(404, "Заказ не найден")
    return order


@app.patch("/orders/{order_id}/status")
async def update_status(order_id: int, status: str, db: AsyncSession = Depends(get_db)):
    order = await db.get(Order, order_id)
    if not order:
        raise HTTPException(404, "Заказ не найден")
    order.status = status
    await db.commit()
    return {"ok": True}


@app.delete("/orders/{order_id}")
async def delete_order(order_id: int, db: AsyncSession = Depends(get_db)):
    order = await db.get(Order, order_id)
    if not order:
        raise HTTPException(404, "Заказ не найден")
    await db.delete(order)
    await db.commit()
    return {"ok": True}


# ==================== FAVORITES ====================
@app.post("/favorites", response_model=FavoriteOut)
async def add_favorite(data: FavoriteCreate, db: AsyncSession = Depends(get_db)):
    fav = Favorite(**data.model_dump())
    db.add(fav)
    await db.commit()
    await db.refresh(fav)
    return fav


@app.get("/favorites/{user_id}", response_model=list[FavoriteOut])
async def get_favorites(user_id: int, db: AsyncSession = Depends(get_db)):
    result = await db.execute(select(Favorite).where(Favorite.user_id == user_id))
    return result.scalars().all()


@app.delete("/favorites/{fav_id}")
async def delete_favorite(fav_id: int, db: AsyncSession = Depends(get_db)):
    fav = await db.get(Favorite, fav_id)
    if not fav:
        raise HTTPException(404, "Избранное не найдено")
    await db.delete(fav)
    await db.commit()
    return {"ok": True}


# ==================== PROMOTIONS ====================
@app.post("/promotions", response_model=PromotionOut)
async def create_promotion(data: PromotionCreate, db: AsyncSession = Depends(get_db)):
    promo = Promotion(**data.model_dump())
    db.add(promo)
    await db.commit()
    await db.refresh(promo)
    return promo


@app.get("/promotions/{user_id}", response_model=list[PromotionOut])
async def get_promotions(user_id: int, db: AsyncSession = Depends(get_db)):
    result = await db.execute(select(Promotion).where(Promotion.user_id == user_id))
    return result.scalars().all()


@app.delete("/promotions/{promo_id}")
async def delete_promotion(promo_id: int, db: AsyncSession = Depends(get_db)):
    promo = await db.get(Promotion, promo_id)
    if not promo:
        raise HTTPException(404, "Акция не найдена")
    await db.delete(promo)
    await db.commit()
    return {"ok": True}


# ==================== LOYALTY ====================
@app.post("/loyalty", response_model=LoyaltyOut)
async def create_loyalty(data: LoyaltyCreate, db: AsyncSession = Depends(get_db)):
    user = await db.get(User, data.user_id)
    if not user:
        raise HTTPException(404, "Пользователь не найден")

    if data.operation_type == "accrual":
        user.balance_points += data.points
    elif data.operation_type == "spend":
        if user.balance_points < data.points:
            raise HTTPException(400, "Недостаточно баллов")
        user.balance_points -= data.points
    elif data.operation_type == "refund":
        user.balance_points += data.points
    else:
        raise HTTPException(400, "Тип операции: accrual / spend / refund")

    tx = LoyaltyTransaction(**data.model_dump())
    db.add(tx)
    await db.commit()
    await db.refresh(tx)
    return tx


@app.get("/loyalty/{user_id}", response_model=list[LoyaltyOut])
async def get_loyalty(user_id: int, db: AsyncSession = Depends(get_db)):
    result = await db.execute(
        select(LoyaltyTransaction).where(LoyaltyTransaction.user_id == user_id)
    )
    return result.scalars().all()