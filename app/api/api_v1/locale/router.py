"""
ルーター（言語API）
"""

from typing import Union

from fastapi import APIRouter, Request

from app.core.i18n import i18n

router = APIRouter()


@router.get(
    "/locales",
    summary="利用可能な言語一覧 取得API",
    description="利用可能な言語一覧を取得します。",
    operation_id="locale_get_available_locales",
)
async def get_available_locales(
    request: Request,
) -> dict[str, Union[list[str], str]]:
    """
    利用可能な言語一覧 取得API

    :param request: リクエストデータ
    :return: レスポンスデータ
    """
    current_locale = request.session.get("locale", "ja")
    return {"locales": i18n.get_available_locales(), "current": current_locale}


@router.get(
    "/locale",
    summary="現在の言語設定 取得API",
    description="現在の言語設定を取得します。",
    operation_id="locale_get_current_locale",
)
async def get_current_locale(request: Request) -> dict[str, str]:
    """
    現在の言語設定 取得API

    :param request: リクエストデータ
    :return: レスポンスデータ
    """
    current_locale = request.session.get("locale", "ja")
    return {"locale": current_locale}


@router.post(
    "/locale",
    summary="言語設定 保存API",
    description="言語設定を保存します。",
    operation_id="locale_set_locale",
)
async def set_locale(
    request: Request,
) -> dict[str, Union[bool, str]]:
    """
    言語設定 保存API

    :param request: リクエストデータ
    :return: レスポンスデータ
    """

    try:
        data = await request.json()
        locale = data.get("locale")
        if locale and locale in i18n.get_available_locales():
            request.session["locale"] = locale
            return {"success": True, "locale": locale}
        else:
            return {"success": False, "error": "Invalid locale"}
    except Exception as e:
        return {"success": False, "error": str(e)}
