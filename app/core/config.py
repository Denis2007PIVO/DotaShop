from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    database_url: str = "sqlite:///./dota_market.db"
    secret_key: str = "super_secret_dota_key"

    # Добавляем те поля, которые у тебя есть в .env,
    # чтобы Pydantic не ругался
    app_name: str = "Dota Market"
    debug: bool = True
    starting_balance: float = 1000.0

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        extra="ignore"  # <-- это разрешит любые другие переменные в .env
    )


# Создаём один экземпляр настроек
settings = Settings()


# На случай, если где-то используется get_settings() — оставим функцию
def get_settings() -> Settings:
    return settings