from abc import ABC

from fastapi import status
from pydantic import Field

from app.schemas import BaseSchema

__all__ = [
    "BaseResponseSchema",
]


class BaseResponseSchema(BaseSchema, ABC):
    """
    基底レスポンススキーマ
    """

    code: int | None = Field(
        default=status.HTTP_200_OK,
        description="HTTPステータスコード",
    )

    message: str | None = Field(
        default="Success",
        description="メッセージ",
    )
