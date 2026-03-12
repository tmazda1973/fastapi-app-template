import logging
import traceback
import uuid
from datetime import datetime, timezone
from typing import Callable, Union

from accessify import private
from fastapi import HTTPException, Request, Response, status
from fastapi.exceptions import RequestValidationError
from fastapi.responses import HTMLResponse, JSONResponse
from fastapi.templating import Jinja2Templates
from sqlalchemy.exc import SQLAlchemyError
from starlette.exceptions import HTTPException as StarletteHTTPException
from starlette.middleware.base import BaseHTTPMiddleware

from app.core.exception import (
    AccessDeniedException,
    BadRequestException,
    HTTPNotFoundException,
    ServerErrorException,
    UnauthorizedException,
)
from app.core.i18n.manager import i18n
from app.enums.base_enum import get_current_locale
from app.schemas.error_response import APIErrorDetail

logger = logging.getLogger(__name__)


class ErrorHandlerMiddleware(BaseHTTPMiddleware):
    """
    エラーハンドリングミドルウェア
    """

    def __init__(self, app, *args, **kwargs):
        super().__init__(app, *args, **kwargs)
        self.templates = Jinja2Templates(directory="app/templates")

    @private
    def _is_api_request(self, request: Request) -> bool:
        """
        APIリクエストかどうかを判定します。

        :param request: リクエスト
        :return: True: APIリクエスト, False: それ以外
        """

        path = request.url.path
        return (
            path.startswith("/api/")
            or path.startswith("/docs")
            or path.startswith("/redoc")
            or path.startswith("/openapi.json")
            or "application/json" in request.headers.get("accept", "")
        )

    async def dispatch(self, request: Request, call_next: Callable) -> Response:
        """
        リクエスト処理とエラーハンドリング
        """

        # リクエストIDを生成
        request_id = str(uuid.uuid4())
        request.state.request_id = request_id

        try:
            response = await call_next(request)
            return response
        except Exception as exc:
            return await self.handle_exception(request, exc, request_id)

    async def handle_exception(
        self,
        request: Request,
        exc: Exception,
        request_id: str,
    ) -> Union[JSONResponse, HTMLResponse]:
        """
        例外ハンドラ

        :param request: リクエスト
        :param exc: 例外
        :param request_id: リクエストID
        :return: エラーレスポンス
        """

        # ログ出力
        error_trace = traceback.format_exc()
        logger.error(
            f"Request ID: {request_id} | "
            f"Path: {request.url.path} | "
            f"Method: {request.method} | "
            f"Error: {str(exc)} | "
            f"Trace: {error_trace}"
        )
        if isinstance(exc, RequestValidationError):
            raise exc

        # 例外タイプ別の処理
        if isinstance(exc, BadRequestException):
            return self._create_error_response(
                request=request,
                status_code=exc.status_code,
                error_code=str(exc.error_code),
                message=exc.message or "Bad Request",
                request_id=request_id,
                details=self._format_validation_errors(exc.errors),
            )

        elif isinstance(exc, UnauthorizedException):
            return self._create_error_response(
                request=request,
                status_code=exc.status_code,
                error_code=str(exc.error_code),
                message=exc.message or "Unauthorized",
                request_id=request_id,
            )

        elif isinstance(exc, AccessDeniedException):
            return self._create_error_response(
                request=request,
                status_code=exc.status_code,
                error_code=str(exc.error_code),
                message=exc.message or "Access Denied",
                request_id=request_id,
            )

        elif isinstance(exc, HTTPNotFoundException):
            return self._create_error_response(
                request=request,
                status_code=exc.status_code,
                error_code=str(exc.error_code),
                message=exc.message or "Not Found",
                request_id=request_id,
            )

        elif isinstance(exc, ServerErrorException):
            return self._create_error_response(
                request=request,
                status_code=exc.status_code,
                error_code=str(exc.error_code),
                message=exc.message or "Internal Server Error",
                request_id=request_id,
            )

        elif isinstance(exc, SQLAlchemyError):
            return self._create_error_response(
                request=request,
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                error_code="DATABASE_ERROR",
                message="Database operation failed",
                request_id=request_id,
            )

        elif isinstance(exc, ValueError):
            return self._create_error_response(
                request=request,
                status_code=status.HTTP_400_BAD_REQUEST,
                error_code="VALIDATION_ERROR",
                message=str(exc),
                request_id=request_id,
            )

        elif isinstance(exc, (HTTPException, StarletteHTTPException)):
            # FastAPI/StarletteのHTTPException (404, 405など)
            error_code = self._get_error_code_from_status(exc.status_code)
            return self._create_error_response(
                request=request,
                status_code=exc.status_code,
                error_code=error_code,
                message=exc.detail if hasattr(exc, "detail") else str(exc),
                request_id=request_id,
            )

        else:
            # 予期しない例外
            return self._create_error_response(
                request=request,
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                error_code="UNEXPECTED_ERROR",
                message="An unexpected error occurred",
                request_id=request_id,
            )

    @private
    def _create_error_response(
        self,
        request: Request,
        status_code: int,
        error_code: str,
        message: str,
        request_id: str,
        details: list[APIErrorDetail] = None,
    ) -> Union[JSONResponse, HTMLResponse]:
        """
        エラーレスポンスを作成します。

        :param request: リクエスト
        :param status_code: ステータスコード
        :param error_code: エラーコード
        :param message: メッセージ
        :param request_id: リクエストID
        :param details: 詳細
        :return: エラーレスポンス
        """

        # APIリクエストかウェブページリクエストかを判定
        if self._is_api_request(request):
            return self._create_json_error_response(
                status_code, error_code, message, request_id, details
            )
        else:
            return self._create_html_error_response(
                status_code, error_code, message, request_id
            )

    @private
    def _create_json_error_response(
        self,
        status_code: int,
        error_code: str,
        message: str,
        request_id: str,
        details: list[APIErrorDetail] = None,
    ) -> JSONResponse:
        """
        JSONエラーレスポンスを作成します。

        :param status_code: ステータスコード
        :param error_code: エラーコード
        :param message: メッセージ
        :param request_id: リクエストID
        :param details: 詳細
        :return: JSONエラーレスポンス
        """

        current_time = datetime.now(timezone.utc)
        content = {
            "success": False,
            "error_code": error_code,
            "message": message,
            "details": [detail.model_dump() for detail in details] if details else None,
            "timestamp": current_time.isoformat(),
            "trace_id": str(uuid.uuid4()),
            "request_id": request_id,
        }

        return JSONResponse(status_code=status_code, content=content)

    @private
    def _create_html_error_response(
        self,
        status_code: int,
        error_code: str,
        message: str,
        request_id: str,
    ) -> HTMLResponse:
        """
        HTMLエラーレスポンスを作成します。

        :param status_code: ステータスコード
        :param error_code: エラーコード
        :param message: メッセージ
        :param request_id: リクエストID
        :return: HTMLエラーレスポンス
        """

        current_time = datetime.now(timezone.utc)
        localized_message = self._localize_message(error_code, message)
        try:
            # Jinja2テンプレートを使用してHTMLを生成
            html_content = self.templates.get_template("error.html").render(
                error_code=error_code,
                message=localized_message,
                timestamp=current_time.strftime("%Y-%m-%d %H:%M:%S"),
                request_id=request_id,
            )
            return HTMLResponse(content=html_content, status_code=status_code)
        except Exception:
            # テンプレートエラーの場合はフォールバック
            fallback_html = """
            <!DOCTYPE html>
            <html>
            <head><title>システムエラー</title></head>
            <body>
                <h1>システムエラーが発生しました</h1>
                <p>申し訳ございませんが、一時的なシステムエラーが発生しています。</p>
                <p>しばらく時間をおいてから再度お試しください。</p>
                <p><a href="/">ホームに戻る</a></p>
            </body>
            </html>
            """
            return HTMLResponse(content=fallback_html, status_code=status_code)

    @private
    def _localize_message(
        self,
        error_code: str,
        _original_message: str | None = None,
    ) -> str:
        """
        メッセージをローカライズします。

        :param error_code: エラーコード
        :param _original_message: 元のメッセージ
        :return: ローカライズされたメッセージ
        """

        try:
            current_locale = get_current_locale()
        except LookupError:
            current_locale = "ja"  # デフォルトロケール

        message_key = f"ui.error_handler.messages.{error_code}"
        translated_message = i18n.t(message_key, locale=current_locale)
        if translated_message == message_key:
            # 翻訳が見つからない
            default_message = i18n.t(
                "ui.error_handler.messages.default",
                locale=current_locale,
            )
            return (
                default_message
                if default_message != "ui.error_handler.messages.default"
                else "システムエラーが発生しました。"
            )

        return translated_message

    @private
    def _get_error_code_from_status(self, status_code: int) -> str:
        """
        HTTPステータスコードからエラーコードを生成します。

        :param status_code: ステータスコード
        :return: エラーコード
        """

        status_code_mapping = {
            400: "BAD_REQUEST",
            401: "UNAUTHORIZED",
            403: "FORBIDDEN",
            404: "NOT_FOUND",
            405: "METHOD_NOT_ALLOWED",
            422: "UNPROCESSABLE_ENTITY",
            500: "INTERNAL_SERVER_ERROR",
        }
        return status_code_mapping.get(status_code, f"HTTP_{status_code}")

    @private
    def _format_validation_errors(
        self, errors: list[dict] = None
    ) -> list[APIErrorDetail]:
        """
        バリデーションエラーをフォーマットします。

        :param errors: バリデーションエラー
        :return: フォーマットされたバリデーションエラー
        """

        if not errors:
            return None

        formatted_errors = []
        for error in errors:
            formatted_errors.append(
                APIErrorDetail(
                    field=error.get("field"),
                    code=error.get("code"),
                    message=error.get("message"),
                )
            )

        return formatted_errors
