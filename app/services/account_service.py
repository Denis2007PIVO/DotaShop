from decimal import Decimal

from sqlalchemy.orm import Session

from app.models import Order, User
from app.repositories import OrderRepository, UserRepository


class AccountService:
    def __init__(self, db: Session) -> None:
        self.db = db
        self.users = UserRepository(db)
        self.orders = OrderRepository(db)

    def get_user(self, user_id: int) -> User:
        user = self.users.get(user_id)
        if user is None:
            raise ValueError("User not found")
        return user

    def top_up(self, user_id: int, amount: Decimal) -> User:
        if amount <= 0:
            raise ValueError("Amount must be positive")
        user = self.get_user(user_id)
        user.balance += amount
        self.db.commit()
        self.db.refresh(user)
        return user

    def history(self, user_id: int) -> list[Order]:
        return self.orders.list_for_user(user_id)
