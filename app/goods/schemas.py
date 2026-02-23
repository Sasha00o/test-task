from pydantic import BaseModel
from typing import Optional


class SProductCreate(BaseModel):
    title: str
    description: Optional[str] = None
    price: float


class SProductUpdate(BaseModel):
    title: Optional[str] = None
    description: Optional[str] = None
    price: Optional[float] = None
