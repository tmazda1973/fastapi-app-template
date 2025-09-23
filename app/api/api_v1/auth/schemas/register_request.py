from pydantic import Field, field_validator

from app.constants.regex_constant import PASSWORD_REGEX
from app.core.i18n.validation_helper import ValidationMessage
from app.schemas.base_response_model import BaseModel

__all__ = [
    "RegisterRequest",
]


class RegisterRequest(BaseModel):
    """
    リクエストスキーマ（ユーザー登録API）
    """

    name: str = Field(..., description="ユーザー名")
    email: str = Field(..., description="メールアドレス")
    password: str = Field(..., description="パスワード")

    @field_validator("name")
    @classmethod
    def validate_name(cls, v: str) -> str:
        """
        バリデーション（名前）
        """

        if not v.strip():
            raise ValueError(ValidationMessage.name_required())

        if len(v.strip()) > 100:
            raise ValueError(ValidationMessage.name_max_length())

        return v.strip()

    @field_validator("password")
    @classmethod
    def validate_password(cls, v: str) -> str:
        """
        バリデーション（パスワード）
        """

        if len(v) < 8:
            raise ValueError(ValidationMessage.password_min_length())

        if not PASSWORD_REGEX.match(v):
            raise ValueError(ValidationMessage.password_pattern())

        return v
