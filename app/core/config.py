from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    app_name: str = "CodeGuard API"
    app_env: str = "development"
    database_url: str

    secret_key: str
    algorithm: str
    access_token_expire_minutes: int

    redis_url: str

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8"
    )


settings = Settings()
