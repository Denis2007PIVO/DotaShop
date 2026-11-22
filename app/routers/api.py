from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import List
from pydantic import BaseModel
from app.db.session import SessionLocal
from app.models.item import Item

# 1. Схема Pydantic для описания того, как будет выглядеть предмет в JSON
class ItemResponse(BaseModel):
    id: int
    name: str
    hero: str
    rarity: str
    price: float
    stock: int

    class Config:
        from_attributes = True  # Позволяет Pydantic читать данные из SQLAlchemy моделей

# 2. Создаем роутер с префиксом /api
router = APIRouter(prefix="/api", tags=["API"])

# 3. Функция для подключения к БД
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

# 4. Эндпоинт для получения всех предметов
@router.get("/items", response_model=List[ItemResponse])
def get_items_api(db: Session = Depends(get_db)):
    """
    Получить список всех доступных предметов (JSON API).
    Используется для интеграции с другими программами.
    """
    items = db.query(Item).filter(Item.stock > 0).all()
    return items

# 5. Эндпоинт для получения одного предмета по ID
@router.get("/items/{item_id}", response_model=ItemResponse)
def get_item_api(item_id: int, db: Session = Depends(get_db)):
    """
    Получить информацию о конкретном предмете по его ID.
    """
    item = db.query(Item).filter(Item.id == item_id).first()
    if not item:
        raise HTTPException(status_code=404, detail="Предмет не найден")
    return item