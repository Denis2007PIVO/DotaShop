from datetime import datetime
from sqlalchemy import String, Float, ForeignKey, DateTime, func, Integer
from sqlalchemy.orm import Mapped, mapped_column, relationship
from app.db.base import Base

class Item(Base):
    __tablename__ = "items"

    id: Mapped[int] = mapped_column(primary_key=True)
    name: Mapped[str] = mapped_column(String(100), index=True)
    hero: Mapped[str] = mapped_column(String(50))
    rarity: Mapped[str] = mapped_column(String(30))
    price: Mapped[float] = mapped_column(Float)
    stock: Mapped[int] = mapped_column(Integer, default=1)
    seller_id: Mapped[int] = mapped_column(ForeignKey("users.id", ondelete="CASCADE"))
    created_at: Mapped[datetime] = mapped_column(DateTime, server_default=func.now())

    seller: Mapped["User"] = relationship(back_populates="items")
    # CartItem не обязательно указывать здесь обратную связь, если мы не используем item.cart_items