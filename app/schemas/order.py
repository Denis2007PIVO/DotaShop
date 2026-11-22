from datetime import datetime
from decimal import Decimal

from pydantic import BaseModel, ConfigDict


class OrderLineRead(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    item_id: int
    quantity: int
    unit_price: Decimal


class OrderRead(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    total: Decimal
    status: str
    created_at: datetime
    lines: list[OrderLineRead]
