from sqlalchemy.orm import Session
from app.models.item import Item

class ItemRepository:
    def __init__(self, db: Session):
        self.db = db

    def get_all(self) -> list[Item]:
        return self.db.query(Item).filter(Item.stock > 0).all()

    def get_by_id(self, item_id: int) -> Item | None:
        return self.db.query(Item).filter(Item.id == item_id).first()