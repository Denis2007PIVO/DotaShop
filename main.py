from fastapi import FastAPI, Request, Depends
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from fastapi.responses import RedirectResponse
from sqlalchemy.orm import Session

# Импортируем все роутеры
from app.routers import auth, market, api
from app.db.session import SessionLocal
from app.models.user import User
from app.services.market_service import MarketService

app = FastAPI(title="Dota Market", description="Маркетплейс предметов Dota 2")

# Подключаем статику (CSS)
app.mount("/static", StaticFiles(directory="app/static"), name="static")

templates = Jinja2Templates(directory="app/templates")

# Подключаем роутеры
app.include_router(auth.router)
app.include_router(market.router)
app.include_router(api.router)


# Функция для получения сессии БД
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


@app.get("/")
def read_root(
        request: Request,
        search: str = None,
        rarity: str = None,
        sort: str = None,
        db: Session = Depends(get_db)
):
    # Проверяем авторизацию
    user_id = request.cookies.get("user_id")
    if not user_id:
        return RedirectResponse(url="/login", status_code=302)

    user = db.query(User).filter(User.id == int(user_id)).first()
    if not user:
        return RedirectResponse(url="/login", status_code=302)

    # Используем сервис для получения отфильтрованных товаров
    service = MarketService(db)
    items = service.get_filtered_items(search, rarity, sort)

    return templates.TemplateResponse(
        request=request,
        name="index.html",
        context={
            "user": user,
            "items": items,
            "search_query": search or "",
            "current_rarity": rarity or "All",
            "current_sort": sort or ""
        }
    )


if __name__ == "__main__":
    import uvicorn

    uvicorn.run("main:app", host="127.0.0.1", port=8000, reload=True)