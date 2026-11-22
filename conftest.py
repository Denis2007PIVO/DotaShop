import pytest
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from app.db.base import Base
from app.models import User, Item, CartItem, Order, OrderLine
from app.core.security import hash_password

# Создаем тестовую базу данных в оперативной памяти
SQLALCHEMY_DATABASE_URL = "sqlite:///:memory:"

engine = create_engine(SQLALCHEMY_DATABASE_URL, connect_args={"check_same_thread": False})
TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

@pytest.fixture(scope="function")
def db_session():
    """Создает чистую базу для каждого теста."""
    Base.metadata.create_all(bind=engine)
    session = TestingSessionLocal()
    try:
        yield session
    finally:
        session.close()
        Base.metadata.drop_all(bind=engine) # Удаляем после теста

@pytest.fixture(scope="function")
def test_user(db_session):
    """Создает тестового пользователя."""
    user = User(
        username="test_user",
        email="test@test.ru",
        hashed_password=hash_password("testpass"),
        balance=1000.0
    )
    db_session.add(user)
    db_session.commit()
    db_session.refresh(user)
    return user

@pytest.fixture(scope="function")
def test_item(db_session, test_user):
    """Создает тестовый предмет."""
    item = Item(
        name="Test Sword",
        hero="Test Hero",
        rarity="Rare",
        price=100.0,
        stock=10,
        seller_id=test_user.id
    )
    db_session.add(item)
    db_session.commit()
    db_session.refresh(item)
    return item