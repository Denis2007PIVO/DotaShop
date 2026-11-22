from sqlalchemy.orm import Session
from app.models.order import Order, OrderLine
from app.models.cart import CartItem
from app.models.item import Item


class OrderRepository:
    def __init__(self, db: Session):
        self.db = db

    def get_user_orders(self, user_id: int) -> list[Order]:
        return self.db.query(Order).filter(Order.user_id == user_id).order_by(Order.created_at.desc()).all()

    def create_order(self, user_id: int, total_price: float, cart_items: list[CartItem]) -> Order:
        order = Order(user_id=user_id, total_price=total_price)
        self.db.add(order)
        self.db.flush()  # Чтобы получить order.id

        for cart_item in cart_items:
            # Берем актуальную цену предмета
            item = self.db.query(Item).filter(Item.id == cart_item.item_id).first()
            line = OrderLine(
                order_id=order.id,
                item_id=cart_item.item_id,
                quantity=cart_item.quantity,
                price_at_purchase=item.price
            )
            self.db.add(line)

            # Уменьшаем остаток на складе
            item.stock -= cart_item.quantity

        self.db.commit()
        self.db.refresh(order)
        return order