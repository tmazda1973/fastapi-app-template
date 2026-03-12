from datetime import datetime

from pydantic import Field

from app.schemas.base_schema import BaseSchema

__all__ = [
    "DeleteResponseSchema",
]


class DeleteResponseSchema(BaseSchema):
    """
    削除レスポンススキーマ
    """

    id: int = Field(..., description="ID")
    deleted_at: datetime = Field(..., description="削除日時")
