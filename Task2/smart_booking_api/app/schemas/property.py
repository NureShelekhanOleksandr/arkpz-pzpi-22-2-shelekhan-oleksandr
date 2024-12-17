from pydantic import BaseModel
from typing import Optional


class PropertyBase(BaseModel):
    name: str
    description: Optional[str]
    rooms: int
    price: float
    location: Optional[str]


class PropertyCreate(PropertyBase):
    pass


class PropertyUpdate(PropertyBase):
    name: Optional[str] = None
    description: Optional[str] = None
    rooms: Optional[int] = None
    price: Optional[float] = None
    location: Optional[str] = None


class Property(PropertyBase):
    id: int
    owner_id: int

    class Config:
        orm_mode = True
