from typing import Any

from .base_response_model import BaseModel

__all__ = [
    "ValidationError",
]


class ValidationError(BaseModel):
    """
    バリデーションエラー情報
    """

    field: str
    code: str
    message: str | None = None
    value: Any | None = None
