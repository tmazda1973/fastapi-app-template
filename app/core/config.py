from pathlib import Path
from typing import Any, Literal, Optional

from pydantic import ValidationInfo, field_validator
from pydantic_settings import BaseSettings
from sqlalchemy.engine import URL

PROJECT_DIR = Path(__file__).parent.parent.parent


class Settings(BaseSettings):
    ENV: Literal["PROD", "STG", "DEV", "LOCAL", "TEST"] | None = "PROD"
    LOG_LEVEL: Literal["DEBUG", "INFO", "WARNING", "ERROR", "CRITICAL"] | None = (
        "WARNING"
    )
    IS_SQL_LOGGING: bool | None = False  # SQLAlchemyクエリログ 出力可否

    # Master DB config
    DB_CONNECTION: Optional[str]
    DB_HOST: Optional[str]
    DB_PORT: Optional[str]
    DB_DATABASE: Optional[str]
    DB_USERNAME: Optional[str]
    DB_PASSWORD: Optional[str]
    SQLALCHEMY_DATABASE_URL: str = ""

    # Read DB config
    READ_DB_CONNECTION: Optional[str]
    READ_DB_HOST: Optional[str]
    READ_DB_PORT: Optional[str]
    READ_DB_DATABASE: Optional[str]
    READ_DB_USERNAME: Optional[str]
    READ_DB_PASSWORD: Optional[str]
    SQLALCHEMY_READ_DATABASE_URL: str = ""

    # Auth config
    SECRET_KEY: Optional[str] = (
        "your-secret-key-for-development"  # セッション用シークレットキー
    )
    JWT_SECRET_KEY: Optional[str]
    JWT_ALGORITHM: Optional[str]
    ACCESS_TOKEN_EXPIRE_MINUTES: Optional[int] = 60 * 14  # 14時間
    RESET_PASSWORD_EXPIRES_MINUTES: Optional[int] = 15  # 15分
    REFRESH_TOKEN_EXPIRE_MINUTES: Optional[int] = 60 * 24 * 30  # 30日
    INVITE_TOKEN_EXPIRE_MINUTES: Optional[int] = 60 * 24  # 24時間

    # Mail config
    MAIL_USERNAME: Optional[str]
    MAIL_PASSWORD: Optional[str]
    MAIL_FROM: Optional[str]
    MAIL_PORT: Optional[int]
    MAIL_SERVER: Optional[str]
    MAIL_FROM_NAME: Optional[str]

    # Frontend config
    FRONTEND_URL: Optional[str] = "http://localhost:8000"

    # Feature flags
    ENABLE_USER_INVITATION: bool = True  # ユーザー招待機能の有効/無効

    @field_validator("SQLALCHEMY_DATABASE_URL")
    @classmethod
    def assemble_db_connection(
        cls,
        v: Optional[str],
        values: ValidationInfo,
    ) -> Any:
        if isinstance(v, str) and v:
            return v

        if not (connection := values.data["DB_CONNECTION"]):
            raise ValueError(
                "must specify at least DB_CONNECTION or SQLALCHEMY_DATABASE_URL",
            )

        username = values.data.get("DB_USERNAME")
        password = values.data.get("DB_PASSWORD")
        host = values.data.get("DB_HOST")
        port = values.data.get("DB_PORT")
        database = values.data.get("DB_DATABASE")

        return URL(
            connection, username, password, host, port, database, []
        ).render_as_string(False)

    @field_validator("SQLALCHEMY_READ_DATABASE_URL")
    @classmethod
    def assemble_read_db_connection(
        cls,
        v: Optional[str],
        values: ValidationInfo,
    ) -> Any:
        if isinstance(v, str) and v:
            return v

        if not (connection := values.data.get("READ_DB_CONNECTION")):
            raise ValueError(
                "must specify at least READ_DB_CONNECTION or SQLALCHEMY_READ_DATABASE_URL",
            )

        username = values.data.get("READ_DB_USERNAME")
        password = values.data.get("READ_DB_PASSWORD")
        host = values.data.get("READ_DB_HOST")
        port = values.data.get("READ_DB_PORT")
        database = values.data.get("READ_DB_DATABASE")

        return URL(
            connection, username, password, host, port, database, []
        ).render_as_string(False)

    class Config:
        case_sensitive = True
        env_file = f"{PROJECT_DIR}/.env"
        env_file_encoding = "utf-8"


settings = Settings()
