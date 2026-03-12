import enum
from contextvars import ContextVar
from typing import Any, Self

from sqlalchemy.dialects.postgresql import ENUM as PG_ENUM

__all__ = [
    "BaseEnum",
    "set_current_locale",
    "get_current_locale",
]

# リクエストスコープでロケール情報を管理するためのコンテキスト変数
# デフォルト値を削除してLookupErrorを発生させる
_current_locale: ContextVar[str] = ContextVar("current_locale")


def set_current_locale(locale: str) -> None:
    """
    現在のロケールを設定します。

    :param locale: ロケールコード（例: "ja", "en"）
    """
    _current_locale.set(locale)


def get_current_locale() -> str:
    """
    現在のロケールを取得します。

    :return: ロケールコード
    """
    return _current_locale.get()


class BaseEnum(enum.Enum):
    """
    基底Enumクラス
    """

    @property
    def label(self) -> str:
        """
        現在のロケールに応じたラベルを取得します。

        :return: ローカライズされたラベル
        """
        return self._to_locale(
            self.value,
            locale_mapping=self.locale_mapping(),
            locale=self.get_current_locale(),
        )

    @classmethod
    def locale_mapping(cls) -> dict[str, dict[str, str]]:
        """
        ロケールマッピングを取得します。
        サブクラスでオーバーライドしてください。

        :return: ロケールマッピング辞書
        """
        return {}

    @classmethod
    def get_current_locale(cls) -> str:
        """
        現在のロケールを取得します。
        コンテキスト変数から動的にロケールを取得します。

        :return: ロケールコード
        """
        return get_current_locale()

    @classmethod
    def choices(cls) -> list[tuple[Self, Any]]:
        """
        選択肢リストを取得します。

        :return: 選択肢リスト
        """
        return [(tag, tag.value) for tag in cls]

    @classmethod
    def get_enum(cls, value: str) -> Self:
        """
        Enum値からEnumメンバーを取得します。

        :param value: Enum値
        :return: Enumメンバー
        """

        if value not in cls._value2member_map_:
            raise ValueError(f"Invalid enum value: [{value}]")

        return cls(value)

    @classmethod
    def is_valid(cls, value: str) -> bool:
        return value in cls._value2member_map_

    @classmethod
    def to_locale(
        cls,
        value: str,
        *,
        locale: str | None = "ja",
    ) -> str:
        """
        Enum値をローカライズします。

        :param value: Enum
        :param locale: ロケールコード（例: "ja", "en"）
        :return: ローカライズ後のEnum値
        """

        return cls._to_locale(
            value,
            locale_mapping=cls.locale_mapping(),
            locale=locale,
            default=cls.default_value(locale=locale),
        )

    @classmethod
    def default_value(cls, *, locale: str = "ja") -> str:
        value = "不明"
        if locale == "en":
            value = "Unknown"

        return value

    @classmethod
    def _to_locale(
        cls,
        value: str,
        *,
        locale_mapping: dict[str, dict[str, str]],
        locale: str | None = "ja",
        default: str | None = "unknown enum",
    ) -> str:
        """
        ローカライズされたEnum値を取得します。

        :param value: Enum値
        :param locale_mapping: マッピング定義
        :param locale: ロケールコード（例: "ja", "en"）
        :param default: デフォルト値
        :return: ローカライズされた名前
        """
        if value not in cls._value2member_map_:
            return default or "unknown enum"

        return locale_mapping.get(value, {}).get(locale, default or "unknown enum")

    @classmethod
    def locale_choices(
        cls,
        *,
        locale: str | None = "ja",
    ) -> list[tuple[Self, str]]:
        """
        ローカライズされた選択肢リストを取得します。

        :param locale: ロケールコード（例: "ja", "en"）
        :return: ローカライズされた選択肢リスト
        """
        return cls._locale_choices(
            locale=locale,
            locale_mapping=cls.locale_mapping(),
        )

    @classmethod
    def _locale_choices(
        cls,
        *,
        locale: str | None = "ja",
        locale_mapping: dict[str, dict[str, str]],
    ) -> list[tuple[Self, Any]]:
        """
        ローカライズされた選択肢リストを取得します。

        :param locale: ロケールコード（例: "ja", "en"）
        :param locale_mapping: マッピング定義
        :return: ローカライズされた選択肢リスト
        """
        return [
            (
                tag,
                cls._to_locale(
                    tag.value,
                    locale=locale,
                    locale_mapping=locale_mapping,
                ),
            )
            for tag in cls
        ]

    @classmethod
    def sa_enum_type(cls) -> PG_ENUM:
        """
        SQLAlchemy Enum型を取得します。

        :return: Enum型
        """
        return PG_ENUM(
            *[e.value for e in cls],
            name=cls.sa_enum_name(),
            create_type=False,
            checkfirst=True,
        )

    @classmethod
    def sa_enum_name(cls) -> str:
        """
        SQLAlchemy Enum名を取得します。

        :return: Enum名
        """
        raise NotImplementedError("Subclasses must implement sa_enum_name")
