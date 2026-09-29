from datetime import datetime
from sqlalchemy import String, Integer, Numeric, DateTime, ForeignKey, Boolean, func
from sqlalchemy.orm import Mapped, mapped_column, relationship
from database import Base


class User(Base):
    __tablename__ = "users"

    id: Mapped[int] = mapped_column(primary_key=True)
    name: Mapped[str] = mapped_column(String(100))
    phone: Mapped[str] = mapped_column(String(20), unique=True)
    balance_points: Mapped[int] = mapped_column(Integer, default=0)
    registration_date: Mapped[datetime] = mapped_column(DateTime, server_default=func.now())

    # связи
    orders: Mapped[list["Order"]] = relationship(
        back_populates="user", cascade="all, delete-orphan"
    )
    favorites: Mapped[list["Favorite"]] = relationship(
        back_populates="user", cascade="all, delete-orphan"
    )
    loyalty_transactions: Mapped[list["LoyaltyTransaction"]] = relationship(
        back_populates="user", cascade="all, delete-orphan"
    )
    promotions: Mapped[list["Promotion"]] = relationship(
        back_populates="user", cascade="all, delete-orphan"
    )


class MenuItem(Base):
    __tablename__ = "menu_items"

    id: Mapped[int] = mapped_column(primary_key=True)
    name: Mapped[str] = mapped_column(String(150))
    description: Mapped[str] = mapped_column(String(500), default="")
    price: Mapped[float] = mapped_column(Numeric(10, 2))
    category: Mapped[str] = mapped_column(String(100))
    is_available: Mapped[bool] = mapped_column(Boolean, default=True)

    # связи
    order_items: Mapped[list["OrderItem"]] = relationship(back_populates="menu_item")
    favorites: Mapped[list["Favorite"]] = relationship(back_populates="menu_item")


class Order(Base):
    __tablename__ = "orders"

    id: Mapped[int] = mapped_column(primary_key=True)
    user_id: Mapped[int] = mapped_column(ForeignKey("users.id"))
    date: Mapped[datetime] = mapped_column(DateTime, server_default=func.now())
    total: Mapped[float] = mapped_column(Numeric(10, 2), default=0)
    status: Mapped[str] = mapped_column(String(30), default="new")
    delivery_method: Mapped[str] = mapped_column(String(30), default="pickup")

    # связи
    user: Mapped["User"] = relationship(back_populates="orders")
    items: Mapped[list["OrderItem"]] = relationship(
        back_populates="order", cascade="all, delete-orphan"
    )
    loyalty_transactions: Mapped[list["LoyaltyTransaction"]] = relationship(
        back_populates="order"
    )


class OrderItem(Base):
    __tablename__ = "order_items"

    id: Mapped[int] = mapped_column(primary_key=True)
    order_id: Mapped[int] = mapped_column(ForeignKey("orders.id"))
    menu_item_id: Mapped[int] = mapped_column(ForeignKey("menu_items.id"))
    quantity: Mapped[int] = mapped_column(Integer, default=1)
    drink_options: Mapped[str] = mapped_column(String(300), default="")
    price: Mapped[float] = mapped_column(Numeric(10, 2))

    # связи
    order: Mapped["Order"] = relationship(back_populates="items")
    menu_item: Mapped["MenuItem"] = relationship(back_populates="order_items")


class Favorite(Base):
    __tablename__ = "favorites"

    id: Mapped[int] = mapped_column(primary_key=True)
    user_id: Mapped[int] = mapped_column(ForeignKey("users.id"))
    menu_item_id: Mapped[int] = mapped_column(ForeignKey("menu_items.id"))
    added_date: Mapped[datetime] = mapped_column(DateTime, server_default=func.now())

    # связи
    user: Mapped["User"] = relationship(back_populates="favorites")
    menu_item: Mapped["MenuItem"] = relationship(back_populates="favorites")


class Promotion(Base):
    __tablename__ = "promotions"

    id: Mapped[int] = mapped_column(primary_key=True)
    user_id: Mapped[int] = mapped_column(ForeignKey("users.id"))
    description: Mapped[str] = mapped_column(String(500))
    discount: Mapped[float] = mapped_column(Numeric(5, 2))
    start_date: Mapped[datetime] = mapped_column(DateTime)
    end_date: Mapped[datetime] = mapped_column(DateTime)
    status: Mapped[str] = mapped_column(String(30), default="active")

    # связи
    user: Mapped["User"] = relationship(back_populates="promotions")


class LoyaltyTransaction(Base):
    __tablename__ = "loyalty_transactions"

    id: Mapped[int] = mapped_column(primary_key=True)
    user_id: Mapped[int] = mapped_column(ForeignKey("users.id"))
    order_id: Mapped[int] = mapped_column(ForeignKey("orders.id"), nullable=True)
    points: Mapped[int] = mapped_column(Integer)
    operation_type: Mapped[str] = mapped_column(String(30))  # accrual / spend / refund
    date: Mapped[datetime] = mapped_column(DateTime, server_default=func.now())

    # связи
    user: Mapped["User"] = relationship(back_populates="loyalty_transactions")
    order: Mapped["Order"] = relationship(back_populates="loyalty_transactions")