from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env")

    database_url: str = "sqlite:///./users.db"
    app_name: str = "User Management API"
    app_version: str = "1.0.0"
    debug: bool = True


settings = Settings()
