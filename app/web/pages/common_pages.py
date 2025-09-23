"""
ページルーター（共通）
"""

from fastapi import APIRouter, Request, status
from fastapi.responses import RedirectResponse

router = APIRouter()


@router.get(
    "/",
    response_model=None,
    summary="ホームページ",
    description="ホームページを表示します。",
    operation_id="home_page",
)
async def home(request: Request) -> RedirectResponse:
    """
    ホームページ

    :param request: リクエストデータ
    :return: リダイレクトレスポンス
    """

    user = request.session.get("user")
    if user:
        # ログイン済み
        return RedirectResponse(
            url="/dashboard",
            status_code=status.HTTP_302_FOUND,
        )

    # 未ログイン
    return RedirectResponse(
        url="/login",
        status_code=status.HTTP_302_FOUND,
    )
