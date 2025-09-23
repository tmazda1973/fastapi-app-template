"""
ロケール関連のヘルパー関数
"""

from fastapi import Request

from app.core.i18n.manager import i18n

__all__ = [
    "get_user_locale_from_request",
    "get_i18n_data_for_response",
]


def parse_accept_language(
    accept_language: str,
    available_locales: list[str],
) -> str | None:
    """
    Accept-Languageヘッダーを解析して最適なロケールを返します。

    :param accept_language: Accept-Languageヘッダーの値
    :param available_locales: 利用可能なロケールのリスト
    :return: 最適なロケール（見つからない場合はNone）
    """

    if not accept_language:
        return None

    # 言語と品質値のペアを解析
    languages = []
    for lang_range in accept_language.split(","):
        lang_range = lang_range.strip()
        if ";q=" in lang_range:
            language, quality = lang_range.split(";q=", 1)
            try:
                quality_value = float(quality)
            except ValueError:
                quality_value = 1.0
        else:
            language = lang_range
            quality_value = 1.0

        language = language.strip().lower()

        # 言語コードの正規化（en-US -> en）
        if "-" in language:
            base_language = language.split("-")[0]
        else:
            base_language = language

        languages.append((base_language, quality_value))

    # 品質値で降順ソート
    languages.sort(key=lambda x: x[1], reverse=True)

    # 利用可能な言語で最初にマッチするものを返す
    for language, _ in languages:
        if language in available_locales:
            return language

    return None


def get_user_locale_from_request(request: Request) -> str:
    """
    リクエストからユーザーロケールを取得します。

    :param request: FastAPIのRequest
    :return: ロケール（デフォルト: "ja"）
    """

    available_locales = ["ja", "en"]

    # 1. URLクエリパラメータから取得
    locale = request.query_params.get("locale")
    if locale and locale in available_locales:
        return locale

    # 2. セッションから取得
    locale = request.session.get("locale")
    if locale and locale in available_locales:
        return locale

    # 3. Cookieから取得
    locale = request.cookies.get("locale")
    if locale and locale in available_locales:
        return locale

    # 4. Accept-Languageヘッダーから取得（品質値を考慮）
    accept_language = request.headers.get("accept-language", "")
    parsed_locale = parse_accept_language(accept_language, available_locales)
    if parsed_locale:
        return parsed_locale

    # 5. デフォルト
    return "ja"


def get_i18n_data_for_response(locale: str) -> dict:
    """
    レスポンス用のi18nデータを取得します。

    :param locale: ロケール
    :return: 翻訳データと言語情報
    """

    locale_data = i18n._translations.get(locale, {})
    translations = {}

    if "ui" in locale_data:
        translations["ui"] = locale_data["ui"]

    if "message" in locale_data and "errors" in locale_data["message"]:
        translations["errors"] = locale_data["message"]["errors"]

    return {
        "locale": locale,
        "translations": translations,
        "available_locales": ["ja", "en"],
    }
