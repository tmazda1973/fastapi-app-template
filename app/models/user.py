from datetime import datetime
from typing import TYPE_CHECKING

from sqlalchemy import TIMESTAMP, Column, Index, Integer, String, text
from sqlmodel import Field, Relationship

from app.enums.user import RoleEnum, VerifyStatusEnum
from app.models.custom_types import EnumType

from .base_model import BaseModel

if TYPE_CHECKING:
    from app.models.password_reset import PasswordResetToken

__all__ = [
    "User",
]


class User(BaseModel, table=True):
    """
    ユーザー
    """

    __tablename__ = "users"

    name: str = Field(
        sa_column=Column(
            String(255),
            nullable=False,
            comment="名前",
        ),
    )

    email: str = Field(
        sa_column=Column(
            String(255),
            nullable=False,
            unique=True,
            comment="メールアドレス",
        ),
    )

    role: RoleEnum = Field(
        sa_column=Column(
            EnumType(RoleEnum, name=RoleEnum.sa_enum_name()),
            nullable=False,
            comment="権限",
        ),
    )

    password: str = Field(
        sa_column=Column(
            String(255),
            nullable=False,
            comment="パスワード",
        ),
    )

    verify_status: VerifyStatusEnum = Field(
        sa_column=Column(
            EnumType(
                VerifyStatusEnum,
                name=VerifyStatusEnum.sa_enum_name(),
                create_type=True,
            ),
            nullable=False,
            server_default=VerifyStatusEnum.unverified.value,
            comment="認証ステータス",
        ),
    )

    reset_password_token: str | None = Field(
        sa_column=Column(
            String(755),
            nullable=True,
            server_default=None,
            comment="パスワードリセットトークン",
        ),
    )

    reset_password_expires: int | None = Field(
        sa_column=Column(
            Integer,
            nullable=True,
            server_default=None,
            comment="パスワードリセット有効期限",
        ),
    )

    invite_token: str | None = Field(
        sa_column=Column(
            String(755),
            nullable=True,
            server_default=None,
            comment="招待トークン",
        ),
    )

    invite_expires: int | None = Field(
        sa_column=Column(
            Integer,
            nullable=True,
            server_default=None,
            comment="招待トークン有効期限",
        ),
    )

    last_login_at: datetime | None = Field(
        sa_column=Column(
            TIMESTAMP(timezone=True),
            nullable=True,
            server_default=None,
            comment="最終ログイン日時",
        ),
    )

    # リレーション（SQLModel推奨方法）
    password_reset_tokens: list["PasswordResetToken"] = Relationship(
        back_populates="user", sa_relationship_kwargs={"cascade": "all, delete-orphan"}
    )

    __table_args__ = (
        Index("idx_users_deleted_at", "deleted_at"),
        Index("idx_users_name", "name"),
        Index(
            "idx_users_email_active",
            "email",
            unique=True,
            postgresql_where=text("deleted_at IS NULL"),
        ),
        {
            "comment": "ユーザー",
        },
    )
