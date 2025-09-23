from typing import Any, Self

from app.core.errors.codes import ERROR_I18N_MAPPING, ErrorCode
from app.core.i18n.manager import i18n

__all__ = [
    "ErrorMessage",
]


class ErrorMessage:
    """
    エラーメッセージ（i18n対応ラッパークラス）

    使用例:
        ErrorMessage(ErrorCode.VALIDATION_ERROR).value
        ErrorMessage(ErrorCode.USER_EMAIL_EXISTS, locale="en").value
        ErrorMessage(ErrorCode.USER_NOT_FOUND, user_id=123).value
    """

    def __init__(
        self,
        error_code: ErrorCode,
        locale: str | None = None,
        **format_kwargs: Any,
    ):
        """
        コンストラクタ

        :param error_code: エラーコード
        :param locale: ロケール（省略時はデフォルト）
        :param format_kwargs: メッセージフォーマット用の引数
        """
        self.error_code = error_code
        self.locale = locale
        self.format_kwargs = format_kwargs

    @property
    def value(self) -> str:
        """
        i18n対応されたエラーメッセージを取得します。

        :return: ローカライズされたエラーメッセージ
        """
        i18n_key = ERROR_I18N_MAPPING.get(self.error_code)
        if i18n_key:
            return i18n.t(i18n_key, self.locale, **self.format_kwargs)

        return f"Unknown error: {self.error_code.value}"

    @property
    def key(self) -> str:
        """
        i18nキーを取得します。

        :return: i18nキー
        """
        return ERROR_I18N_MAPPING.get(self.error_code, "")

    def __str__(self) -> str:
        return self.value

    def __repr__(self) -> str:
        return f"ErrorMessage({self.error_code}, locale={self.locale}, value='{self.value}')"

    def with_locale(self, locale: str) -> Self:
        """
        ロケールを指定します。

        :param locale: 新しいロケール
        :return: 自インスタンス
        """
        return ErrorMessage(self.error_code, locale, **self.format_kwargs)

    def with_params(self, **kwargs: Any) -> Self:
        """
        フォーマットパラメータを指定します。

        :param kwargs: フォーマットパラメータ
        :return: 自インスタンス
        """
        new_kwargs = {**self.format_kwargs, **kwargs}
        return ErrorMessage(self.error_code, self.locale, **new_kwargs)
