import hashlib
from datetime import datetime
from sqlalchemy import String, Integer, Numeric, DateTime, ForeignKey, Boolean, func
from sqlalchemy.orm import Mapped, mapped_column, relationship
from pydantic import BaseModel, ConfigDict

from database import Base


# ============================================================
#                        USER
# ============================================================
class User(Base):
    __tablename__ = "users"

    id: Mapped[int] = mapped_column(primary_key=True)
    name: Mapped[str] = mapped_column(String(100))
    phone: Mapped[str] = mapped_column(String(20), unique=True)
    password_hash: Mapped[str] = mapped_column(String(64))          # ← новый столбец
    balance_points: Mapped[int] = mapped_column(Integer, default=0)
    registration_date: Mapped[datetime] = mapped_column(DateTime, server_default=func.now())

    orders: Mapped[list["Order"]] = relationship(back_populates="user", cascade="all, delete-orphan")
    favorites: Mapped[list["Favorite"]] = relationship(back_populates="user", cascade="all, delete-orphan")
    loyalty: Mapped[list["LoyaltyTransaction"]] = relationship(back_populates="user", cascade="all, delete-orphan")
    promotions: Mapped[list["Promotion"]] = relationship(back_populates="user", cascade="all, delete-orphan")


# --- хеширование пароля ---
def hash_password(password: str) -> str:
    return hashlib.sha256(password.encode("utf-8")).hexdigest()


# --- схемы User ---
class UserCreate(BaseModel):
    name: str
    phone: str
    password: str                       # ← принимаем пароль при регистрации

class LoginData(BaseModel):
    phone: str
    password: str


class UserOut(BaseModel):
    id: int
    name: str
    phone: str
    balance_points: int
    registration_date: datetime
    model_config = ConfigDict(from_attributes=True)


class LoginData(BaseModel):             # ← для эндпоинта /login
    phone: str
    password: str



# ============================================================
#                       MENU ITEM
# ============================================================
class MenuItem(Base):
    __tablename__ = "menu_items"

    id: Mapped[int] = mapped_column(primary_key=True)
    name: Mapped[str] = mapped_column(String(150))
    description: Mapped[str] = mapped_column(String(500), default="")
    price: Mapped[float] = mapped_column(Numeric(10, 2))
    category: Mapped[str] = mapped_column(String(100))
    is_available: Mapped[bool] = mapped_column(Boolean, default=True)

    order_items: Mapped[list["OrderItem"]] = relationship(back_populates="menu_item")


class MenuItemCreate(BaseModel):
    name: str
    description: str = ""
    price: float
    category: str
    is_available: bool = True


class MenuItemOut(MenuItemCreate):
    id: int
    model_config = ConfigDict(from_attributes=True)


# ============================================================
#                        ORDER
# ============================================================
class Order(Base):
    __tablename__ = "orders"

    id: Mapped[int] = mapped_column(primary_key=True)
    user_id: Mapped[int] = mapped_column(ForeignKey("users.id"))
    date: Mapped[datetime] = mapped_column(DateTime, server_default=func.now())
    total: Mapped[float] = mapped_column(Numeric(10, 2), default=0)
    status: Mapped[str] = mapped_column(String(30), default="new")
    delivery_method: Mapped[str] = mapped_column(String(30), default="pickup")

    user: Mapped["User"] = relationship(back_populates="orders")
    items: Mapped[list["OrderItem"]] = relationship(back_populates="order", cascade="all, delete-orphan")


class OrderItemCreate(BaseModel):
    menu_item_id: int
    quantity: int = 1
    drink_options: str = ""


class OrderCreate(BaseModel):
    user_id: int
    delivery_method: str = "pickup"
    items: list[OrderItemCreate] = []


class OrderOut(BaseModel):
    id: int
    user_id: int
    date: datetime
    total: float
    status: str
    delivery_method: str
    model_config = ConfigDict(from_attributes=True)


# ============================================================
#                      ORDER ITEM
# ============================================================
class OrderItem(Base):
    __tablename__ = "order_items"

    id: Mapped[int] = mapped_column(primary_key=True)
    order_id: Mapped[int] = mapped_column(ForeignKey("orders.id"))
    menu_item_id: Mapped[int] = mapped_column(ForeignKey("menu_items.id"))
    quantity: Mapped[int] = mapped_column(Integer, default=1)
    drink_options: Mapped[str] = mapped_column(String(300), default="")
    price: Mapped[float] = mapped_column(Numeric(10, 2))

    order: Mapped["Order"] = relationship(back_populates="items")
    menu_item: Mapped["MenuItem"] = relationship(back_populates="order_items")


class OrderItemOut(BaseModel):
    id: int
    menu_item_id: int
    quantity: int
    drink_options: str
    price: float
    model_config = ConfigDict(from_attributes=True)


class OrderFull(BaseModel):
    id: int
    user_id: int
    date: datetime
    total: float
    status: str
    delivery_method: str
    items: list[OrderItemOut] = []
    model_config = ConfigDict(from_attributes=True)


# ============================================================
#                       FAVORITE
# ============================================================
class Favorite(Base):
    __tablename__ = "favorites"

    id: Mapped[int] = mapped_column(primary_key=True)
    user_id: Mapped[int] = mapped_column(ForeignKey("users.id"))
    menu_item_id: Mapped[int] = mapped_column(ForeignKey("menu_items.id"))
    added_date: Mapped[datetime] = mapped_column(DateTime, server_default=func.now())

    user: Mapped["User"] = relationship(back_populates="favorites")


class FavoriteCreate(BaseModel):
    user_id: int
    menu_item_id: int


class FavoriteOut(FavoriteCreate):
    id: int
    added_date: datetime
    model_config = ConfigDict(from_attributes=True)


# ============================================================
#                      PROMOTION
# ============================================================
class Promotion(Base):
    __tablename__ = "promotions"

    id: Mapped[int] = mapped_column(primary_key=True)
    user_id: Mapped[int] = mapped_column(ForeignKey("users.id"))
    description: Mapped[str] = mapped_column(String(500))
    discount: Mapped[float] = mapped_column(Numeric(5, 2))
    start_date: Mapped[datetime] = mapped_column(DateTime)
    end_date: Mapped[datetime] = mapped_column(DateTime)
    status: Mapped[str] = mapped_column(String(30), default="active")

    user: Mapped["User"] = relationship(back_populates="promotions")


class PromotionCreate(BaseModel):
    user_id: int
    description: str
    discount: float
    start_date: datetime
    end_date: datetime


class PromotionOut(PromotionCreate):
    id: int
    status: str
    model_config = ConfigDict(from_attributes=True)


# ============================================================
#                  LOYALTY TRANSACTION
# ============================================================
class LoyaltyTransaction(Base):
    __tablename__ = "loyalty_transactions"

    id: Mapped[int] = mapped_column(primary_key=True)
    user_id: Mapped[int] = mapped_column(ForeignKey("users.id"))
    order_id: Mapped[int | None] = mapped_column(ForeignKey("orders.id"), nullable=True)
    points: Mapped[int] = mapped_column(Integer)
    operation_type: Mapped[str] = mapped_column(String(30))
    date: Mapped[datetime] = mapped_column(DateTime, server_default=func.now())

    user: Mapped["User"] = relationship(back_populates="loyalty")


class LoyaltyCreate(BaseModel):
    user_id: int
    order_id: int | None = None
    points: int
    operation_type: str


class LoyaltyOut(LoyaltyCreate):
    id: int
    date: datetime
    model_config = ConfigDict(from_attributes=True)