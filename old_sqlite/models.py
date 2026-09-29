from datetime import datetime
from typing import Annotated

from sqlalchemy import DateTime, Float, Integer, String, Text, func
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column

from database import Base  # или определите Base прямо здесь, см. ниже


# ============================================================
# ПЕРЕИСПОЛЬЗУЕМЫЕ ТИПЫ (Annotated)
# ============================================================

# Первичный ключ: int + primary_key + index + автоинкремент
int_pk = Annotated[int, mapped_column(Integer, primary_key=True, index=True)]

# Числа
int_required = Annotated[int, mapped_column(Integer, nullable=False)]

# Строки фиксированной длины
str_100_unique = Annotated[str, mapped_column(String(100), unique=True, index=True)]
str_100 = Annotated[str, mapped_column(String(100), index=True)]
# str_150 = Annotated[str, mapped_column(String(150), index=True)]
# str_255 = Annotated[str, mapped_column(String(255))]
# str_500_opt = Annotated[str | None, mapped_column(String(500), nullable=True)]

# Текст
text_opt = Annotated[str | None, mapped_column(Text, nullable=True)]

# Дата/время
# datetime_created = Annotated[
#     datetime,
#     mapped_column(DateTime(timezone=True), server_default=func.now()),
# ]


# ============================================================
# МОДЕЛИ
# ============================================================

class User(Base):
    __tablename__ = "users"

    id: Mapped[int_pk]
    name: Mapped[str_100_unique]
    password: Mapped[str_100]


class Dish(Base):
    __tablename__ = "dishes"

    id: Mapped[int_pk]
    name: Mapped[str_100_unique]
    category: Mapped[str_100]
    price: Mapped[int_required]
    description: Mapped[text_opt]
    foto: Mapped[text_opt]