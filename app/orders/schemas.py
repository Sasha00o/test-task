import uuid
from pydantic import BaseModel


class SOrderCreate(BaseModel):
    good_id: uuid.UUID
    quantity: int
    delivery_address: str
