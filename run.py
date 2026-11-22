import os
import subprocess
import sys
from pathlib import Path


def run_command(command):
    """Вспомогательная функция для запуска команд в терминале."""
    print(f"--> Выполняю: {command}")
    result = subprocess.run(command, shell=True)
    if result.returncode != 0:
        print(f"❌ Ошибка при выполнении: {command}")
        sys.exit(1)


def main():
    print("🚀 Запуск Dota Market (режим 'Включил и забыл')...")

    # 1. Проверяем, существует ли файл базы данных
    db_file = Path("dota_market.db")
    if not db_file.exists():
        print("📦 База данных не найдена. Применяем миграции Alembic...")
        run_command("alembic upgrade head")
    else:
        print("✅ База данных уже существует.")
        # На всякий случай применяем миграции (вдруг появились новые)
        run_command("alembic upgrade head")

    # 2. Запускаем скрипт заполнения (seed)
    print("🌱 Проверяем наличие тестовых данных...")
    run_command("python -m scripts.seed")

    # 3. Запускаем сервер Uvicorn
    print("\n🔥 Всё готово! Запускаю сервер...")
    print("👉 Открой в браузере: http://127.0.0.1:8000\n")

    # Запускаем uvicorn (без флага --reload, чтобы не было проблем с перезагрузкой)
    # Если хочешь разработку с автообновлением, добавь "--reload"
    run_command("uvicorn main:app --host 127.0.0.1 --port 8000")


if __name__ == "__main__":
    main()