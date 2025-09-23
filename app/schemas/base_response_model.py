from datetime import datetime

from fastapi import status
from pydantic import BaseModel as PydanticBaseModel
from pydantic import ConfigDict, EmailStr, Field

from app.utils.common_util import datetime_to_jst_str

__all__ = [
    "BaseModel",
    "BaseResponseModel",
    "EmailSchema",
    "ChangePasswordSchema",
]


class BaseModel(PydanticBaseModel):
    """
    基底モデル
    """

    model_config = ConfigDict(
        json_encoders={datetime: datetime_to_jst_str},
        populate_by_name=True,
    )

    def to_dict(self) -> dict:
        """
        モデルを辞書に変換します。
        :return: 辞書データ
        """
        return self.model_dump(
            by_alias=True,
            exclude_none=True,
            exclude_unset=True,
        )


class BaseResponseModel(BaseModel):
    """
    基底レスポンスモデル
    """

    code: int | None = Field(
        default=status.HTTP_200_OK,
        description="HTTPステータスコード",
    )
    message: str | None = Field(
        default="Success",
        description="メッセージ",
    )


class EmailSchema(BaseModel):
    email: EmailStr | list[EmailStr] = Field(
        ...,
        description="メールアドレス",
    )


class ChangePasswordSchema(BaseModel):
    password: str = Field(..., description="")
