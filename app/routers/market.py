from fastapi import APIRouter, Depends, Request, Form
from fastapi.responses import RedirectResponse, HTMLResponse
from fastapi.templating import Jinja2Templates
from sqlalchemy.orm import Session
from app.db.session import SessionLocal
from app.models.user import User
from app.models.item import Item
from app.models.cart import CartItem
from app.models.order import Order, OrderLine
from app.repositories.user_repository import UserRepository

router = APIRouter()
templates = Jinja2Templates(directory="app/templates")


def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


# Вспомогательная функция для получения юзера из куки
def get_current_user(request: Request, db: Session):
    user_id = request.cookies.get("user_id")
    if not user_id:
        return None
    return db.query(User).filter(User.id == int(user_id)).first()


# 1. Добавление в корзину
@router.post("/cart/add/{item_id}")
def add_to_cart(item_id: int, request: Request, db: Session = Depends(get_db)):
    user = get_current_user(request, db)
    if not user:
        return RedirectResponse(url="/login", status_code=302)

    # Проверяем, есть ли уже этот товар в корзине
    cart_item = db.query(CartItem).filter(CartItem.user_id == user.id, CartItem.item_id == item_id).first()

    if cart_item:
        cart_item.quantity += 1
    else:
        new_cart_item = CartItem(user_id=user.id, item_id=item_id, quantity=1)
        db.add(new_cart_item)

    db.commit()
    return RedirectResponse(url="/cart", status_code=303)  # Перекидываем сразу в корзину


# 2. Страница корзины
@router.get("/cart", response_class=HTMLResponse)
def view_cart(request: Request, db: Session = Depends(get_db)):
    user = get_current_user(request, db)
    if not user:
        return RedirectResponse(url="/login", status_code=302)

    cart_items = db.query(CartItem).filter(CartItem.user_id == user.id).all()
    total_price = sum(item.item.price * item.quantity for item in cart_items)

    return templates.TemplateResponse(
        request=request,
        name="cart.html",
        context={"user": user, "cart_items": cart_items, "total_price": total_price}
    )


# 3. Оформление заказа (Покупка)
@router.post("/cart/checkout")
def checkout(request: Request, db: Session = Depends(get_db)):
    user = get_current_user(request, db)
    if not user:
        return RedirectResponse(url="/login", status_code=302)

    cart_items = db.query(CartItem).filter(CartItem.user_id == user.id).all()
    if not cart_items:
        return RedirectResponse(url="/cart", status_code=303)

    total_price = sum(item.item.price * item.quantity for item in cart_items)

    # Проверяем баланс
    if user.balance < total_price:
        return templates.TemplateResponse(
            request=request,
            name="cart.html",
            context={"user": user, "cart_items": cart_items, "total_price": total_price,
                     "error": "Недостаточно средств!"}
        )

    # Списываем деньги
    user.balance -= total_price

    # Создаем заказ
    new_order = Order(user_id=user.id, total_price=total_price)
    db.add(new_order)
    db.flush()  # Чтобы получить ID заказа

    # Переносим товары в заказ и уменьшаем остатки
    for c_item in cart_items:
        order_line = OrderLine(
            order_id=new_order.id,
            item_id=c_item.item_id,
            quantity=c_item.quantity,
            price_at_purchase=c_item.item.price
        )
        db.add(order_line)

        # Уменьшаем склад
        c_item.item.stock -= c_item.quantity

        # Удаляем из корзины
        db.delete(c_item)

    db.commit()
    return RedirectResponse(url="/history", status_code=303)  # Перекидываем в историю


# 4. Пополнение баланса
@router.post("/balance/topup")
def topup_balance(request: Request, amount: float = Form(...), db: Session = Depends(get_db)):
    user = get_current_user(request, db)
    if user and amount > 0:
        user.balance += amount
        db.commit()
    return RedirectResponse(url="/", status_code=303)


# 5. История покупок
@router.get("/history", response_class=HTMLResponse)
def history(request: Request, db: Session = Depends(get_db)):
    user = get_current_user(request, db)
    if not user:
        return RedirectResponse(url="/login", status_code=302)

    orders = db.query(Order).filter(Order.user_id == user.id).order_by(Order.created_at.desc()).all()

    return templates.TemplateResponse(
        request=request,
        name="history.html",
        context={"user": user, "orders": orders}
    )