from sqlalchemy.orm import Session
from app.models.user import User
from app.core.security import hash_password  # <--- Импортируем hash_password

class UserRepository:
    def __init__(self, db: Session):
        self.db = db

    def get_by_username(self, username: str) -> User | None:
        return self.db.query(User).filter(User.username == username).first()

    def create(self, username: str, email: str, password: str) -> User:
        user = User(
            username=username,
            email=email,
            hashed_password=hash_password(password), # <--- Теперь вызывается правильно
            balance=1000.0
        )
        self.db.add(user)
        self.db.commit()
        self.db.refresh(user)
        return user

    def update_balance(self, user_id: int, amount: float) -> User:
        user = self.db.query(User).filter(User.id == user_id).first()
        if user:
            user.balance += amount
            self.db.commit()
            self.db.refresh(user)
        return user