from datetime import datetime
from pydantic import BaseModel, ConfigDict


# ==================== USER ====================
class UserCreate(BaseModel):
    name: str
    phone: str


class UserOut(BaseModel):
    id: int
    name: str
    phone: str
    balance_points: int
    registration_date: datetime
    model_config = ConfigDict(from_attributes=True)


class UserShort(BaseModel):
    id: int
    name: str
    phone: str
    model_config = ConfigDict(from_attributes=True)


# ==================== MENU ====================
class MenuItemCreate(BaseModel):
    name: str
    description: str = ""
    price: float
    category: str
    is_available: bool = True


class MenuItemOut(MenuItemCreate):
    id: int
    model_config = ConfigDict(from_attributes=True)


class MenuItemShort(BaseModel):
    id: int
    name: str
    price: float
    model_config = ConfigDict(from_attributes=True)


# ==================== ORDER ====================
class OrderItemCreate(BaseModel):
    menu_item_id: int
    quantity: int = 1
    drink_options: str = ""


class OrderCreate(BaseModel):
    user_id: int
    delivery_method: str = "pickup"
    items: list[OrderItemCreate] = []


class OrderItemOut(BaseModel):
    id: int
    menu_item_id: int
    quantity: int
    drink_options: str
    price: float
    model_config = ConfigDict(from_attributes=True)


class OrderItemFull(BaseModel):
    id: int
    quantity: int
    drink_options: str
    price: float
    menu_item: MenuItemShort
    model_config = ConfigDict(from_attributes=True)


class OrderOut(BaseModel):
    id: int
    user_id: int
    date: datetime
    total: float
    status: str
    delivery_method: str
    model_config = ConfigDict(from_attributes=True)


class OrderFull(BaseModel):
    id: int
    date: datetime
    total: float
    status: str
    delivery_method: str
    user: UserShort
    items: list[OrderItemFull]
    model_config = ConfigDict(from_attributes=True)


# ==================== FAVORITE ====================
class FavoriteCreate(BaseModel):
    user_id: int
    menu_item_id: int


class FavoriteOut(FavoriteCreate):
    id: int
    added_date: datetime
    model_config = ConfigDict(from_attributes=True)


class FavoriteFull(BaseModel):
    id: int
    added_date: datetime
    menu_item: MenuItemShort
    model_config = ConfigDict(from_attributes=True)


# ==================== PROMOTION ====================
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


# ==================== LOYALTY ====================
class LoyaltyCreate(BaseModel):
    user_id: int
    order_id: int | None = None
    points: int
    operation_type: str  # accrual / spend / refund


class LoyaltyOut(LoyaltyCreate):
    id: int
    date: datetime
    model_config = ConfigDict(from_attributes=True)


class LoyaltyFull(BaseModel):
    id: int
    points: int
    operation_type: str
    date: datetime
    order_id: int | None = None
    model_config = ConfigDict(from_attributes=True)