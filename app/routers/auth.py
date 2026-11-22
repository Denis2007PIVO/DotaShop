from fastapi import APIRouter, Depends, Request, Form, status
from fastapi.responses import HTMLResponse, RedirectResponse
from fastapi.templating import Jinja2Templates
from sqlalchemy.orm import Session
from app.db.session import SessionLocal
from app.repositories.user_repository import UserRepository
from app.core.security import verify_password, hash_password  # Добавил hash_password
from app.models.user import User  # <--- ВАЖНО: импорт модели User

router = APIRouter()
templates = Jinja2Templates(directory="app/templates")


def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


@router.get("/login", response_class=HTMLResponse)
def login_page(request: Request):
    return templates.TemplateResponse(request=request, name="login.html")


@router.get("/register", response_class=HTMLResponse)
def register_page(request: Request):
    return templates.TemplateResponse(request=request, name="register.html")


@router.post("/login")
def login(request: Request, username: str = Form(...), password: str = Form(...), db: Session = Depends(get_db)):
    repo = UserRepository(db)
    username = username.strip()
    password = password.strip()
    user = repo.get_by_username(username)

    if not user or not verify_password(password, user.hashed_password):
        return templates.TemplateResponse(request=request, name="login.html",
                                          context={"error": "Неверный логин или пароль"})

    response = RedirectResponse(url="/", status_code=status.HTTP_302_FOUND)
    response.set_cookie(key="user_id", value=str(user.id), httponly=True)
    return response


@router.get("/logout")
def logout():
    response = RedirectResponse(url="/register", status_code=status.HTTP_302_FOUND)
    response.delete_cookie("user_id")
    return response


@router.post("/register")
def register(
        request: Request,
        username: str = Form(...),
        email: str = Form(...),
        password: str = Form(...),
        db: Session = Depends(get_db)
):
    repo = UserRepository(db)
    username = username.strip()
    email = email.strip()
    password = password.strip()

    # Проверяем, нет ли уже такого пользователя
    if repo.get_by_username(username):
        return templates.TemplateResponse(
            request=request, name="register.html",
            context={"error": "Пользователь с таким логином уже существует"}
        )

    # Создаем нового юзера (используем репозиторий)
    new_user = repo.create(username=username, email=email, password=password)

    if new_user:
        response = RedirectResponse(url="/", status_code=status.HTTP_302_FOUND)
        response.set_cookie(key="user_id", value=str(new_user.id), httponly=True)
        return response

    return templates.TemplateResponse(
        request=request, name="register.html",
        context={"error": "Ошибка при создании пользователя"}
    )