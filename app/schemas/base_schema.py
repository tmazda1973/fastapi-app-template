from abc import ABC
from datetime import datetime

from pydantic import BaseModel as PydanticBaseModel
from pydantic import ConfigDict

from app.utils.common_util import datetime_to_jst_str

__all__ = [
    "BaseSchema",
]


class BaseSchema(PydanticBaseModel, ABC):
    """
    基底スキーマ
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
