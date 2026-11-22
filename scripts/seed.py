from app.db.session import SessionLocal
from app.models import User, Item
from app.core.security import hash_password


def seed() -> None:
    with SessionLocal() as session:
        # Проверяем, есть ли уже пользователи
        if session.query(User).count() > 0:
            print("✅ База уже заполнена, пропускаем сид.")
            return

        print("🌱 База пуста. Заполняем тестовыми данными...")

        # Создаем пользователей
        alice = User(
            username="alice",
            email="alice@dota.ru",
            hashed_password=hash_password("password123"),
            balance=10000.0
        )
        bob = User(
            username="bob",
            email="bob@dota.ru",
            hashed_password=hash_password("password456"),
            balance=500.0
        )
        session.add_all([alice, bob])
        session.flush()

        # Создаем предметы
        items_data = [
            ("Daedalus", "Phantom Assassin", "Legendary", 320.0, 5, alice.id),
            ("Aghanim's Scepter", "Invoker", "Immortal", 180.0, 2, alice.id),
            ("Black King Bar", "Sven", "Rare", 95.5, 10, bob.id),
            ("Blink Dagger", "Axe", "Common", 50.0, 20, alice.id),
            ("Battle Fury", "Anti-Mage", "Legendary", 410.0, 3, bob.id),
            ("Manta Style", "Juggernaut", "Rare", 130.0, 8, alice.id),
            ("Satanic", "Wraith King", "Immortal", 550.0, 1, alice.id),
            ("Eye of Skadi", "Drow Ranger", "Legendary", 290.0, 4, bob.id),
            ("Scythe of Vyse", "Lion", "Immortal", 400.0, 2, alice.id),
            ("Radiance", "Spectre", "Legendary", 350.0, 6, bob.id),
            ("Butterfly", "Ember Spirit", "Rare", 280.0, 7, alice.id),
            ("Desolator", "Templar Assassin", "Legendary", 310.0, 4, bob.id),
            ("Shivas Guard", "Timbersaw", "Rare", 270.0, 5, alice.id),
            ("Linken's Sphere", "Morphling", "Rare", 250.0, 9, alice.id),
            ("Mjollnir", "Faceless Void", "Legendary", 340.0, 3, bob.id),
            ("Silver Edge", "Slark", "Rare", 210.0, 6, alice.id),
            ("Aegis of the Immortal", "Roshan", "Immortal", 999.0, 1, bob.id),
            ("Refresher Orb", "Enigma", "Legendary", 380.0, 2, alice.id),
            ("Heart of Tarrasque", "Bristleback", "Legendary", 360.0, 4, bob.id),
            ("Divine Rapier", "Kunkka", "Immortal", 1200.0, 1, alice.id),
        ]

        items = [
            Item(
                name=name,
                hero=hero,
                rarity=rarity,
                price=price,
                stock=stock,
                seller_id=seller_id
            )
            for name, hero, rarity, price, stock, seller_id in items_data
        ]

        session.add_all(items)
        session.commit()

        print("✅ Данные успешно добавлены!")
        print(f"📦 Загружено предметов: {len(items)}")
        print("👤 Логины: alice / password123 (баланс 10000$), bob / password456")


if __name__ == "__main__":
    seed()