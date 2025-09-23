from datetime import datetime, timedelta, timezone
from typing import TYPE_CHECKING, Optional

from sqlalchemy import Boolean, Column, DateTime, ForeignKey, Integer, String
from sqlmodel import Field, Relationship

from app.models.base_model import BaseModel

if TYPE_CHECKING:
    from app.models.user import User

__all__ = [
    "PasswordResetToken",
]


class PasswordResetToken(BaseModel, table=True):
    """
    パスワードリセットトークン
    """

    __tablename__ = "password_reset_tokens"

    user_id: int = Field(
        sa_column=Column(
            Integer,
            ForeignKey("users.id"),
            nullable=False,
            comment="ユーザーID",
        ),
    )

    token: str = Field(
        sa_column=Column(
            String(255),
            nullable=False,
            unique=True,
            index=True,
            comment="リセットトークン",
        ),
    )

    reset_code: str = Field(
        sa_column=Column(
            String(10),
            nullable=False,
            index=True,
            comment="リセットコード",
        ),
    )

    expires_at: datetime = Field(
        sa_column=Column(
            DateTime(timezone=True),
            nullable=False,
            comment="有効期限",
        ),
    )

    is_used: bool = Field(
        sa_column=Column(
            Boolean,
            nullable=False,
            default=False,
            comment="使用済みフラグ",
        ),
    )

    used_at: Optional[datetime] = Field(
        sa_column=Column(
            DateTime(timezone=True),
            nullable=True,
            comment="使用日時",
        ),
    )

    # リレーション（SQLModel推奨方法）
    user: "User" = Relationship(back_populates="password_reset_tokens")

    def is_expired(self) -> bool:
        """
        トークンが期限切れであるかを判定します。

        :return: True: 期限切れ, False: 期限切れではない
        """
        return datetime.now(timezone.utc) > self.expires_at

    def is_valid(self) -> bool:
        """
        トークンが有効かどうかを判定します。

        :return: True: 有効, False: 無効
        """
        return not self.is_used and not self.is_expired()

    def mark_as_used(self) -> None:
        """
        トークンを使用済みとしてマークします。

        :return: None
        """
        self.is_used = True
        self.used_at = datetime.now(timezone.utc)

    @classmethod
    def create_token(
        cls,
        user_id: int,
        token: str,
        reset_code: str,
        expires_in_minutes: int = 30,
    ) -> "PasswordResetToken":
        """
        新しいリセットトークンを作成します。

        :param user_id: ユーザーID
        :param token: トークン文字列
        :param reset_code: リセットコード
        :param expires_in_minutes: 有効期限（分）
        :return: パスワードリセットトークン
        """

        expires_at = datetime.now(timezone.utc) + timedelta(minutes=expires_in_minutes)
        return cls(
            user_id=user_id,
            token=token,
            reset_code=reset_code,
            expires_at=expires_at,
        )
