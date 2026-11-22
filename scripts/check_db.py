from app.db.session import SessionLocal
from app.models import User


def check():
    with SessionLocal() as session:
        users = session.query(User).all()
        print(f"Всего пользователей в базе: {len(users)}")
        for u in users:
            print(f"ID: {u.id} | Логин: {u.username} | Хэш: {u.hashed_password[:20]}...")

        alice = session.query(User).filter(User.username == 'alice').first()
        if alice:
            print("\n--- Проверка пароля для alice ---")
            from app.core.security import verify_password
            is_ok = verify_password("password123", alice.hashed_password)
            print(f"Пароль 'password123' подходит? -> {is_ok}")
        else:
            print("\nПользователь alice НЕ НАЙДЕН в базе!")


if __name__ == "__main__":
    check()