from decimal import Decimal

from pydantic import BaseModel, Field


class CartItemCreate(BaseModel):
    item_id: int
    quantity: int = Field(default=1, ge=1)


class CartLine(BaseModel):
    id: int
    item_id: int
    name: str
    unit_price: Decimal
    quantity: int
    line_total: Decimal


class CartSummary(BaseModel):
    items: list[CartLine]
    total: Decimal
