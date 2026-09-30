# from datetime import datetime
# from pydantic import BaseModel, ConfigDict
#
#
# # ---------- USER ----------
# class UserCreate(BaseModel):
#     name: str
#     phone: str
#
#
# class UserOut(BaseModel):
#     id: int
#     name: str
#     phone: str
#     balance_points: int
#     registration_date: datetime
#     model_config = ConfigDict(from_attributes=True)
#
#
# # ---------- MENU ----------
# class MenuItemCreate(BaseModel):
#     name: str
#     description: str = ""
#     price: float
#     category: str
#     is_available: bool = True
#
#
# class MenuItemOut(MenuItemCreate):
#     id: int
#     model_config = ConfigDict(from_attributes=True)
#
#
# # ---------- ORDER ----------
# class OrderItemCreate(BaseModel):
#     menu_item_id: int
#     quantity: int = 1
#     drink_options: str = ""
#
#
# class OrderCreate(BaseModel):
#     user_id: int
#     delivery_method: str = "pickup"
#     items: list[OrderItemCreate] = []
#
#
# class OrderOut(BaseModel):
#     id: int
#     user_id: int
#     date: datetime
#     total: float
#     status: str
#     delivery_method: str
#     model_config = ConfigDict(from_attributes=True)
#
#
# # ---------- FAVORITE ----------
# class FavoriteCreate(BaseModel):
#     user_id: int
#     menu_item_id: int
#
#
# class FavoriteOut(FavoriteCreate):
#     id: int
#     added_date: datetime
#     model_config = ConfigDict(from_attributes=True)
#
#
# # ---------- PROMOTION ----------
# class PromotionCreate(BaseModel):
#     user_id: int
#     description: str
#     discount: float
#     start_date: datetime
#     end_date: datetime
#
#
# class PromotionOut(PromotionCreate):
#     id: int
#     status: str
#     model_config = ConfigDict(from_attributes=True)
#
#
# # ---------- LOYALTY ----------
# class LoyaltyCreate(BaseModel):
#     user_id: int
#     order_id: int | None = None
#     points: int
#     operation_type: str
#
#
# class LoyaltyOut(LoyaltyCreate):
#     id: int
#     date: datetime
#     model_config = ConfigDict(from_attributes=True)