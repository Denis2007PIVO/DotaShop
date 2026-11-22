from fastapi import Depends
from sqlalchemy.orm import Session
from app.db.session import SessionLocal
from app.repositories.user_repository import UserRepository
from app.repositories.item_repository import ItemRepository
from app.repositories.cart_repository import CartRepository
from app.repositories.order_repository import OrderRepository
from app.services.market_service import MarketService

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

def get_market_service(db: Session = Depends(get_db)) -> MarketService:
    return MarketService(
        user_repo=UserRepository(db),
        item_repo=ItemRepository(db),
        cart_repo=CartRepository(db),
        order_repo=OrderRepository(db)
    )