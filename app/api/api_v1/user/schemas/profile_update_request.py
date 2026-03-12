from pydantic import BaseModel, Field, field_validator

from app.core.i18n.validation_helper import ValidationMessage

__all__ = [
    "ProfileUpdateRequest",
]


class ProfileUpdateRequest(BaseModel):
    """
    リクエストスキーマ（プロフィール更新API）
    """

    name: str = Field(..., description="名前")

    @field_validator("name")
    @classmethod
    def validate_name(cls, v: str) -> str:
        """
        名前のバリデーション
        """
        if not v.strip():
            raise ValueError(ValidationMessage.field_required("name"))

        if len(v.strip()) > 255:
            raise ValueError(ValidationMessage.max_length("name", 255))

        return v.strip()

    class Config:
        json_schema_extra = {"example": {"name": "田中太郎"}}
