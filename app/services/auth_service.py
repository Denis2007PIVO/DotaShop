from decimal import Decimal

from sqlalchemy.orm import Session

from app.core.config import get_settings
from app.core.security import hash_password, verify_password
from app.models import User
from app.repositories import UserRepository
from app.schemas import UserCreate


class AuthService:
    def __init__(self, db: Session) -> None:
        self.db = db
        self.users = UserRepository(db)

    def register(self, data: UserCreate) -> User:
        if self.users.get_by_username(data.username) is not None:
            raise ValueError("Username is already taken")
        if self.users.get_by_email(data.email) is not None:
            raise ValueError("Email is already registered")

        user = User(
            username=data.username,
            email=data.email,
            hashed_password=hash_password(data.password),
            balance=Decimal(str(get_settings().starting_balance)),
        )
        self.users.add(user)
        self.db.commit()
        self.db.refresh(user)
        return user

    def authenticate(self, username: str, password: str) -> User | None:
        user = self.users.get_by_username(username)
        if user is None or not verify_password(password, user.hashed_password):
            return None
        return user
