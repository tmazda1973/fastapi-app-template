"""
バリデーション例外ハンドラ
"""

from fastapi import Request
from fastapi.exceptions import RequestValidationError
from fastapi.responses import JSONResponse

from app.core.i18n.locale_helper import (
    get_i18n_data_for_response,
    get_user_locale_from_request,
)
from app.core.i18n.manager import i18n
from app.enums.base_enum import set_current_locale

__all__ = [
    "validation_exception_handler",
]


def _translate_validation_message(message: str, locale: str) -> str:
    """
    バリデーションメッセージを翻訳します。

    :param message: 元のメッセージ
    :param locale: ロケール
    :return: 翻訳されたメッセージ
    """

    # "Value error, "を除去
    if message.startswith("Value error, "):
        message = message[len("Value error, ") :]

    # 翻訳キーがある場合は実際のメッセージに変換
    if message.startswith("__VALIDATION_KEY__") and message.endswith("__END__"):
        # 翻訳キーとパラメータを抽出
        content = message[len("__VALIDATION_KEY__") : -len("__END__")]
        # パラメータの分離
        parts = content.split("|")
        validation_key = parts[0]
        params = {}
        # パラメータの解析
        for param_part in parts[1:]:
            if ":" in param_part:
                key, value = param_part.split(":", 1)
                params[key] = value

        # フィールド名の翻訳（パラメータにfieldがある場合）
        if "field" in params:
            field_value = params["field"]
            # フィールド値が翻訳キーの形式なら翻訳
            if field_value.startswith("{validation.fields.") and field_value.endswith(
                "}"
            ):
                field_key = field_value[1:-1]  # {} を除去
                field_name = i18n.translate(field_key, locale=locale)
                params["field"] = field_name

        return i18n.translate(validation_key, locale=locale, **params)

    return message


def _build_json_response(error_detail: list, user_locale: str) -> JSONResponse:
    """
    JSON形式のエラーレスポンスを構築します。

    :param error_detail: エラー詳細
    :param user_locale: ユーザーロケール
    :return: JSONResponse
    """

    translated_errors = []
    for error in error_detail:
        error_copy = error.copy()
        message = error_copy.get("msg", "エラーが発生しました")
        error_copy["msg"] = _translate_validation_message(message, user_locale)
        translated_errors.append(error_copy)

    return JSONResponse(
        status_code=422,
        content={"detail": translated_errors},
    )


# POST-onlyルートとそれに対応するGETルートのマッピング
POST_TO_GET_ROUTE_MAPPING = {
    "/auth/login": "/login",
    "/forgot-password": "/forgot-password",
    "/reset-password": "/reset-password",
    "/invite/accept": "/invite/accept",
    # 今後新しいルートが追加された場合、ここに追加する
}


async def _restore_url_for_validation_error(
    request: Request,
    error_detail: list,
) -> str:
    """
    バリデーションエラー用にURLを復元します。
    特定のルートに対してURLパラメータを復元する必要がある場合に使用します。

    :param request: リクエスト
    :param error_detail: エラー詳細（部分的にパースされたデータが含まれる可能性）
    :return: 復元されたURL
    """

    path = request.url.path

    # POST-onlyルートから対応するGETルートへのマッピングをチェック
    if path in POST_TO_GET_ROUTE_MAPPING:
        get_route = POST_TO_GET_ROUTE_MAPPING[path]

        # パラメータ復元が必要な特定のページ
        if path == "/reset-password":
            # パスワードリセットページ: email + token が必要
            parsed_data = {}

            # 方法1: エラー詳細から有効なフィールドを抽出
            for error in error_detail:
                if error.get("input") is not None:
                    field_path = error.get("loc", [])
                    if len(field_path) > 1 and field_path[0] == "body":
                        field_name = field_path[1]
                        if field_name in ["email", "token"]:
                            parsed_data[field_name] = error.get("input")

            # 方法2: リクエストボディから直接JSONをパースを試みる
            if (
                not parsed_data
                or "email" not in parsed_data
                or "token" not in parsed_data
            ):
                try:
                    import json

                    body = await request.body()
                    if body:
                        json_data = json.loads(body.decode("utf-8"))
                        if "email" in json_data:
                            parsed_data["email"] = json_data["email"]
                        if "token" in json_data:
                            parsed_data["token"] = json_data["token"]
                except (json.JSONDecodeError, UnicodeDecodeError, Exception):
                    # JSONパースに失敗した場合は無視
                    pass

            # emailとtokenが取得できた場合、URLパラメータを復元
            if "email" in parsed_data and "token" in parsed_data:
                from urllib.parse import urlencode

                params = urlencode({
                    "email": parsed_data["email"],
                    "token": parsed_data["token"],
                })
                return f"{get_route}?{params}"

        # Refererヘッダーからの復元を試みる（フォールバック）
        referer = request.headers.get("referer", "")
        if "reset-password" in referer and ("token=" in referer or "email=" in referer):
            return referer

        elif path == "/invite/accept":
            # 招待受諾ページ: token のみが必要
            parsed_data = {}

            # 方法1: エラー詳細から有効なフィールドを抽出
            for error in error_detail:
                if error.get("input") is not None:
                    field_path = error.get("loc", [])
                    if len(field_path) > 1 and field_path[0] == "body":
                        field_name = field_path[1]
                        if field_name == "token":
                            parsed_data[field_name] = error.get("input")

            # 方法2: リクエストボディから直接JSONをパースを試みる
            if "token" not in parsed_data:
                try:
                    import json

                    body = await request.body()
                    if body:
                        json_data = json.loads(body.decode("utf-8"))
                        if "token" in json_data:
                            parsed_data["token"] = json_data["token"]
                except (json.JSONDecodeError, UnicodeDecodeError, Exception):
                    # JSONパースに失敗した場合は無視
                    pass

            # tokenが取得できた場合、URLパラメータを復元
            if "token" in parsed_data:
                params = urlencode({"token": parsed_data["token"]})
                return f"{get_route}?{params}"

        # 単純なリダイレクトの場合（パラメータ復元が不要）
        else:
            return get_route

    # デフォルトは現在のURL
    return str(request.url)


async def _build_inertia_response(
    error_detail: list,
    request: Request,
    user_locale: str,
) -> JSONResponse:
    """
    Inertia形式のエラーレスポンスを構築します。

    :param error_detail: エラー詳細
    :param request: リクエスト
    :param user_locale: ユーザーロケール
    :return: JSONResponse
    """

    # エラーを適切なフォーマットに変換
    formatted_errors = {}
    for error in error_detail:
        field_path = error.get("loc", [])
        # bodyやqueryといった親要素を除去
        if len(field_path) > 1 and field_path[0] in ["body", "query", "path"]:
            field_name = field_path[1]
        else:
            field_name = field_path[-1] if field_path else "form"

        message = error.get("msg", "エラーが発生しました")
        formatted_errors[field_name] = _translate_validation_message(
            message, user_locale
        )

    # 現在のコンポーネント名を取得（ヘッダーから）
    current_component = request.headers.get("x-inertia-current-component", "Error")

    # URLを復元（特定のルートでパラメータが必要な場合）
    response_url = await _restore_url_for_validation_error(request, error_detail)

    # Inertia形式のレスポンスを構築する（i18nデータを含む）
    inertia_response = {
        "component": current_component,
        "props": {
            "errors": formatted_errors,
            **get_i18n_data_for_response(user_locale),
        },
        "url": response_url,
        "version": request.headers.get("x-inertia-version", "1"),
    }

    # ヘッダーを設定してレスポンスを返す
    return JSONResponse(
        content=inertia_response,
        status_code=422,
        headers={"X-Inertia": "true", "Content-Type": "application/json"},
    )


async def validation_exception_handler(
    request: Request,
    exc: RequestValidationError,
) -> JSONResponse:
    """
    バリデーション例外ハンドラ

    - バリデーションエラーが発生した場合に、JSONレスポンスを返す。
    - Inertiaリクエストの場合は、Inertia形式のレスポンスを返す。
    - 多言語対応

    :param request: リクエストデータ
    :param exc: バリデーション例外
    :return: JSONレスポンス
    """

    # ユーザーロケールを取得してコンテキストに設定
    user_locale = get_user_locale_from_request(request)
    set_current_locale(user_locale)

    error_detail = exc.errors()
    is_inertia = "x-inertia" in request.headers

    if not is_inertia:
        # 通常のエラーレスポンス（翻訳処理を含む）
        return _build_json_response(error_detail, user_locale)
    else:
        # Inertiaリクエストの場合、POST-onlyルートは自動リダイレクト
        if request.url.path in POST_TO_GET_ROUTE_MAPPING:
            from fastapi.responses import RedirectResponse

            redirect_url = await _restore_url_for_validation_error(
                request, error_detail
            )

            # Inertiaヘッダーを維持してリダイレクト
            response = RedirectResponse(
                url=redirect_url, status_code=302, headers={"X-Inertia": "true"}
            )

            return response
        else:
            # 通常のInertiaレスポンス
            return await _build_inertia_response(error_detail, request, user_locale)
