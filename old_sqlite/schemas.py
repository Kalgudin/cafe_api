from pydantic import BaseModel, ConfigDict, Field


# ==================== USER ====================
class UserBase(BaseModel):
    name: str = Field(..., min_length=2, max_length=100)


class UserCreate(UserBase):
    password: str = Field(..., min_length=4, max_length=100)


class UserUpdate(BaseModel):
    name: str | None = Field(None, min_length=2, max_length=100)
    password: str | None = Field(None, min_length=4, max_length=100)


class UserRead(UserBase):
    """Схема для ответа — без пароля!"""
    model_config = ConfigDict(from_attributes=True)

    id: int


# ==================== DISH ====================
class DishBase(BaseModel):
    name: str = Field(..., min_length=1, max_length=100)
    category: str = Field(..., min_length=1, max_length=100)
    price: int = Field(..., ge=0)
    description: str | None = None
    foto: str | None = None


class DishCreate(DishBase):
    pass


class DishUpdate(BaseModel):
    name: str | None = Field(None, min_length=1, max_length=100)
    category: str | None = Field(None, min_length=1, max_length=100)
    price: int | None = Field(None, ge=0)
    description: str | None = None
    foto: str | None = None
    


class DishRead(DishBase):
    model_config = ConfigDict(from_attributes=True)

    id: int