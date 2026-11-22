from decimal import Decimal
from pathlib import Path

from fastapi import APIRouter, Depends, Form, HTTPException, Request
from fastapi.responses import HTMLResponse, RedirectResponse
from fastapi.templating import Jinja2Templates
from sqlalchemy.orm import Session

from app.db.session import get_db
from app.models import User
from app.routers.deps import get_current_user
from app.services import AccountService

router = APIRouter(tags=["account"])
templates = Jinja2Templates(directory=Path(__file__).resolve().parents[1] / "templates")


@router.get("/balance", response_class=HTMLResponse, name="balance_page")
def balance_page(
    request: Request,
    db: Session = Depends(get_db),
    user: User = Depends(get_current_user),
):
    return templates.TemplateResponse(
        request=request, name="account/balance.html", context={"user": user}
    )


@router.post("/balance", name="top_up")
def top_up(
    request: Request,
    amount: Decimal = Form(...),
    db: Session = Depends(get_db),
    user: User = Depends(get_current_user),
) -> RedirectResponse:
    try:
        AccountService(db).top_up(user.id, amount)
    except ValueError as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc
    return RedirectResponse(url=request.url_for("balance_page"), status_code=303)


@router.get("/history", response_class=HTMLResponse, name="history_page")
def history_page(
    request: Request,
    db: Session = Depends(get_db),
    user: User = Depends(get_current_user),
):
    orders = AccountService(db).history(user.id)
    return templates.TemplateResponse(
        request=request,
        name="account/history.html",
        context={"user": user, "orders": orders},
    )
