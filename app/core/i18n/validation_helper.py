"""
バリデーションメッセージのi18n対応ヘルパー
"""

from app.core.i18n.manager import i18n
from app.enums.base_enum import get_current_locale

__all__ = [
    "ValidationMessage",
]


class ValidationMessage:
    """
    バリデーションメッセージのi18n対応ヘルパークラス
    """

    @staticmethod
    def get(key: str, **kwargs) -> str:
        """
        現在のロケールに対応したバリデーションメッセージを取得します

        :param key: バリデーションメッセージキー
        :param kwargs: フォーマット用のキーワード引数
        :return: ローカライズされたバリデーションメッセージ
        """
        try:
            locale = get_current_locale()

        except LookupError:
            # ロケールが設定されていない場合は翻訳キーを返す
            # バリデーション例外ハンドラーで実際の翻訳を行う
            # パラメータも含めてエンコード
            params = ""
            if kwargs:
                params = "|" + "|".join(f"{k}:{v}" for k, v in kwargs.items())

            translation_key = f"__VALIDATION_KEY__validation.{key}{params}__END__"
            return translation_key

        # validate.ja.jsonから翻訳を取得
        return i18n.translate(f"validation.{key}", locale=locale, **kwargs)

    @staticmethod
    def min_length(field_key: str, min_value: int) -> str:
        """
        最小文字数バリデーションメッセージ

        :param field_key: フィールドキー（例: "password", "name"）
        :param min_value: 最小文字数
        :return: ローカライズされたバリデーションメッセージ
        """
        try:
            locale = get_current_locale()
            field_name = i18n.translate(f"validation.fields.{field_key}", locale=locale)
        except LookupError:
            field_name = f"{{validation.fields.{field_key}}}"

        return ValidationMessage.get("min_length", field=field_name, min=min_value)

    @staticmethod
    def max_length(field_key: str, max_value: int) -> str:
        """
        最大文字数バリデーションメッセージ

        :param field_key: フィールドキー（例: "password", "name"）
        :param max_value: 最大文字数
        :return: ローカライズされたバリデーションメッセージ
        """
        try:
            locale = get_current_locale()
            field_name = i18n.translate(f"validation.fields.{field_key}", locale=locale)
        except LookupError:
            field_name = f"{{validation.fields.{field_key}}}"

        return ValidationMessage.get("max_length", field=field_name, max=max_value)

    @staticmethod
    def min_length_simple(field_key: str, min_value: int) -> str:
        """
        最小文字数バリデーションメッセージ（シンプル）

        :param field_key: フィールドキー（例: "password", "name"）
        :param min_value: 最小文字数
        :return: ローカライズされたバリデーションメッセージ
        """
        try:
            locale = get_current_locale()
            field_name = i18n.translate(f"validation.fields.{field_key}", locale=locale)
        except LookupError:
            field_name = f"{{validation.fields.{field_key}}}"

        return ValidationMessage.get(
            "min_length_simple", field=field_name, min=min_value
        )

    @staticmethod
    def field_required(field_key: str) -> str:
        """
        必須フィールドバリデーションメッセージ

        :param field_key: フィールドキー（例: "password", "name"）
        :return: ローカライズされたバリデーションメッセージ
        """
        try:
            locale = get_current_locale()
            field_name = i18n.translate(f"validation.fields.{field_key}", locale=locale)
        except LookupError:
            field_name = f"{{validation.fields.{field_key}}}"

        return ValidationMessage.get("field_required", field=field_name)

    @staticmethod
    def translate_key(validation_key: str, locale: str = "ja") -> str:
        """
        バリデーションキーを指定されたロケールで翻訳します

        :param validation_key: バリデーションキー（例: "validation.password.complexity"）
        :param locale: ロケール
        :return: 翻訳されたメッセージ
        """
        return i18n.translate(validation_key, locale=locale)

    @staticmethod
    def name_required() -> str:
        """名前必須エラー"""
        return ValidationMessage.get("name.required")

    @staticmethod
    def name_max_length() -> str:
        """名前文字数制限エラー"""
        return ValidationMessage.get("name.max_length")

    @staticmethod
    def email_max_length() -> str:
        """メールアドレス文字数制限エラー"""
        return ValidationMessage.get("email.max_length")

    @staticmethod
    def password_min_length() -> str:
        """パスワード最小文字数エラー"""
        return ValidationMessage.get("password.min_length")

    @staticmethod
    def password_pattern() -> str:
        """パスワードパターンエラー"""
        return ValidationMessage.get("password.pattern")

    @staticmethod
    def password_mismatch() -> str:
        """パスワード不一致エラー"""
        return ValidationMessage.get("password.mismatch")

    @staticmethod
    def password_complexity() -> str:
        """パスワード複雑性エラー"""
        return ValidationMessage.get("password.complexity")

    @staticmethod
    def password_min_length_simple() -> str:
        """パスワード最小文字数エラー（シンプル）"""
        return ValidationMessage.get("password.min_length_simple")

    @staticmethod
    def invite_token_required() -> str:
        """招待トークン必須エラー"""
        return ValidationMessage.get("invite.token_required")
