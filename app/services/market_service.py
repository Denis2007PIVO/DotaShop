from sqlalchemy.orm import Session
from app.models.user import User
from app.models.item import Item
from app.models.cart import CartItem
from app.models.order import Order, OrderLine


class MarketService:
    def __init__(self, db: Session):
        self.db = db

    def get_filtered_items(self, search: str = None, rarity: str = None, sort: str = None):
        query = self.db.query(Item).filter(Item.stock > 0)
        if search:
            query = query.filter(Item.name.ilike(f"%{search}%"))
        if rarity and rarity != "All":
            query = query.filter(Item.rarity == rarity)

        if sort == "asc":
            query = query.order_by(Item.price.asc())
        elif sort == "desc":
            query = query.order_by(Item.price.desc())
        else:
            query = query.order_by(Item.id.asc())
        return query.all()

    def add_to_cart(self, user_id: int, item_id: int):
        cart_item = self.db.query(CartItem).filter(
            CartItem.user_id == user_id, CartItem.item_id == item_id
        ).first()

        if cart_item:
            cart_item.quantity += 1
        else:
            cart_item = CartItem(user_id=user_id, item_id=item_id, quantity=1)
            self.db.add(cart_item)
        self.db.commit()

    def checkout(self, user_id: int) -> tuple[bool, str]:
        user = self.db.query(User).filter(User.id == user_id).first()
        cart_items = self.db.query(CartItem).filter(CartItem.user_id == user_id).all()

        if not cart_items:
            return False, "Корзина пуста"

        total_price = sum(item.item.price * item.quantity for item in cart_items)

        if user.balance < total_price:
            return False, "Недостаточно средств на балансе"

        user.balance -= total_price

        new_order = Order(user_id=user.id, total_price=total_price)
        self.db.add(new_order)
        self.db.flush()

        for c_item in cart_items:
            order_line = OrderLine(
                order_id=new_order.id,
                item_id=c_item.item_id,
                quantity=c_item.quantity,
                price_at_purchase=c_item.item.price
            )
            self.db.add(order_line)
            c_item.item.stock -= c_item.quantity
            self.db.delete(c_item)

        self.db.commit()
        return True, "Успешно"

    def topup_balance(self, user_id: int, amount: float) -> bool:
        if amount <= 0:
            return False
        user = self.db.query(User).filter(User.id == user_id).first()
        if user:
            user.balance += amount
            self.db.commit()
            return True
        return False