from sqlalchemy.dialects.postgresql import ENUM as PG_ENUM
from sqlalchemy.types import TypeDecorator

__all__ = [
    "EnumType",
]


class EnumType(TypeDecorator):
    """
    タイプデコレーター（Enum）
    """

    impl = PG_ENUM
    cache_ok = True

    def __init__(self, enum_class, **kw):
        self.enum_class = enum_class
        values = [e.value for e in enum_class]
        super(EnumType, self).__init__(*values, **kw)

    def process_bind_param(self, value, dialect):
        if value is None:
            return None

        # Enum型オブジェクトから文字列値に変換
        if isinstance(value, self.enum_class):
            return value.value  # type: ignore

        return value

    def process_result_value(self, value, dialect):
        if value is None:
            return None

        # 文字列値からEnum型オブジェクトに変換
        return self.enum_class(value)
