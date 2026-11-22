import pytest
from app.services.market_service import MarketService
from app.models.cart import CartItem
from app.models.order import Order


def test_add_to_cart(db_session, test_user, test_item):
    """Тест: добавление предмета в корзину."""
    service = MarketService(db_session)
    service.add_to_cart(test_user.id, test_item.id)

    # Проверяем, что предмет появился в корзине
    cart_item = db_session.query(CartItem).filter_by(user_id=test_user.id).first()
    assert cart_item is not None
    assert cart_item.quantity == 1
    assert cart_item.item_id == test_item.id


def test_checkout_success(db_session, test_user, test_item):
    """Тест: успешная покупка (списываются деньги, уменьшается склад)."""
    service = MarketService(db_session)

    # Кладем в корзину 2 предмета (цена 100, значит потратим 200)
    service.add_to_cart(test_user.id, test_item.id)
    service.add_to_cart(test_user.id, test_item.id)

    initial_balance = test_user.balance  # 1000
    initial_stock = test_item.stock  # 10

    # Оформляем заказ
    success, message = service.checkout(test_user.id)

    # Проверяем результаты
    assert success is True
    assert test_user.balance == initial_balance - 200  # Должно остаться 800
    assert test_item.stock == initial_stock - 2  # Должно остаться 8

    # Проверяем, что заказ создан и корзина пуста
    order = db_session.query(Order).filter_by(user_id=test_user.id).first()
    assert order is not None
    assert order.total_price == 200
    assert db_session.query(CartItem).filter_by(user_id=test_user.id).count() == 0


def test_checkout_not_enough_money(db_session, test_user, test_item):
    """Тест (пограничное условие): покупка при нехватке денег."""
    service = MarketService(db_session)

    # Делаем пользователя почти банкротом
    test_user.balance = 50.0
    db_session.commit()

    # Кладем в корзину предмет за 100
    service.add_to_cart(test_user.id, test_item.id)

    # Пытаемся купить
    success, message = service.checkout(test_user.id)

    # Проверяем, что покупка не прошла, а деньги не списались
    assert success is False
    assert message == "Недостаточно средств на балансе"
    assert test_user.balance == 50.0
    assert test_item.stock == 10  # Склад не изменился