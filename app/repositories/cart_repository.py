from sqlalchemy.orm import Session
from app.models.cart import CartItem
from app.models.item import Item


class CartRepository:
    def __init__(self, db: Session):
        self.db = db

    def get_user_cart(self, user_id: int) -> list[CartItem]:
        return self.db.query(CartItem).filter(CartItem.user_id == user_id).all()

    def add_to_cart(self, user_id: int, item_id: int) -> None:
        cart_item = self.db.query(CartItem).filter(
            CartItem.user_id == user_id, CartItem.item_id == item_id
        ).first()

        if cart_item:
            cart_item.quantity += 1
        else:
            cart_item = CartItem(user_id=user_id, item_id=item_id, quantity=1)
            self.db.add(cart_item)
        self.db.commit()

    def clear_cart(self, user_id: int) -> None:
        self.db.query(CartItem).filter(CartItem.user_id == user_id).delete()
        self.db.commit()