"""
招待関連リクエストスキーマ
"""

from pydantic import BaseModel, EmailStr, field_validator

from app.constants.regex_constant import PASSWORD_REGEX
from app.core.i18n.validation_helper import ValidationMessage

__all__ = [
    "SendInviteRequest",
    "AcceptInviteRequest",
]


class SendInviteRequest(BaseModel):
    """
    リクエストスキーマ（招待送信API）
    """

    email: EmailStr
    name: str
    role: str | None = None

    @field_validator("name")
    @classmethod
    def validate_name(cls, v: str) -> str:
        """
        名前のバリデーション
        """
        if not v.strip():
            raise ValueError(ValidationMessage.name_required())
        if len(v.strip()) > 100:
            raise ValueError(ValidationMessage.name_max_length())
        return v.strip()

    @field_validator("email")
    @classmethod
    def validate_email(cls, v: EmailStr) -> EmailStr:
        """
        メールアドレスのバリデーション
        """
        if len(str(v)) > 255:
            raise ValueError(ValidationMessage.email_max_length())
        return v


class AcceptInviteRequest(BaseModel):
    """
    招待受諾リクエスト
    """

    token: str
    password: str

    @field_validator("token")
    @classmethod
    def validate_token(cls, v: str) -> str:
        """
        トークンのバリデーション
        """
        if not v.strip():
            raise ValueError(ValidationMessage.invite_token_required())
        return v.strip()

    @field_validator("password")
    @classmethod
    def validate_password(cls, v: str) -> str:
        """
        パスワードのバリデーション
        """
        if len(v) < 8:
            raise ValueError(ValidationMessage.password_min_length())
        if not PASSWORD_REGEX.match(v):
            raise ValueError(ValidationMessage.password_pattern())
        return v
