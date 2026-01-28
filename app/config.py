from pydantic_settings import BaseSettings
from pydantic import field_validator


class Settings(BaseSettings):
    bot_token: str
    admin_ids: list[int] = []

    db_host: str = "localhost"
    db_port: int = 5432
    db_user: str = "household"
    db_password: str = "secret"
    db_name: str = "household"

    @field_validator("admin_ids", mode="before")
    @classmethod
    def parse_admin_ids(cls, v):
        if isinstance(v, str):
            if not v.strip():
                return []
            return [int(x.strip()) for x in v.split(",")]
        return v

    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"


settings = Settings()
