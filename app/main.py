import logging
from collections.abc import Awaitable
from datetime import datetime
from typing import Annotated, Callable

from fastapi import Depends, FastAPI, HTTPException, Request
from fastapi.exceptions import RequestValidationError
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse, HTMLResponse, JSONResponse, Response
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from inertia import (
    Inertia,
    InertiaConfig,
    inertia_dependency_factory,
)
from starlette.exceptions import HTTPException as StarletteHTTPException
from starlette.middleware.base import BaseHTTPMiddleware
from starlette.middleware.sessions import SessionMiddleware

from app.api import api_v1_router
from app.core.config import settings
from app.core.exception import (
    AccessDeniedException,
    BadRequestException,
    HTTPNotFoundException,
    ImportErrorException,
    ServerErrorException,
    UnauthorizedException,
)
from app.core.exception_handlers import validation_exception_handler
from app.core.i18n.manager import i18n
from app.core.middleware.error_handler import ErrorHandlerMiddleware
from app.core.response import (
    AccessDeniedResponse,
    BadRequestResponse,
    ImportErrorResponse,
    NotFoundErrorResponse,
    ServerErrorResponse,
    UnauthorizedResponse,
)
from app.enums.base_enum import get_current_locale
from app.enums.config import EnvEnum
from app.web import web_router

# ログ出力レベル
logging.basicConfig(level=settings.LOG_LEVEL)

# ローカル環境の場合、直接 Uvicorn を起動することになり、ログが二重に出力されるケースもあるため、明示的に伝搬をオフにしておく。
# AWS 環境で動作する場合は Gunicorn 経由での起動になるため、二重出力にはならない。
logger = logging.getLogger("uvicorn")
if settings.ENV == EnvEnum.LOCAL.value:
    logger.propagate = False


class HTTPSRedirectMiddleware(BaseHTTPMiddleware):
    """
    プロダクション環境でHTTPS URLを強制するミドルウェア
    """

    async def dispatch(self, request: Request, call_next):
        # プロダクション環境でHTTPS URLを強制
        if settings.ENV in ["DEV", "STG", "PROD"]:
            # X-Forwarded-Proto ヘッダーをチェック
            forwarded_proto = request.headers.get("x-forwarded-proto", "")

            if forwarded_proto == "http":
                # HTTPSにリダイレクト
                https_url = str(request.url).replace("http://", "https://", 1)
                return Response(
                    status_code=301,
                    headers={"Location": https_url},
                )

            # リクエストスコープを修正してHTTPS URLを強制
            if forwarded_proto == "https":
                request.scope["scheme"] = "https"

        response = await call_next(request)
        return response


app = FastAPI(
    title="FAST API",
    openapi_url="/api/v1/openapi.json",
    docs_url="/api/v1/docs",
    redoc_url="/api/v1/redoc",
)

# エラーハンドリングミドルウェア
app.add_middleware(ErrorHandlerMiddleware)
# HTTPS強制ミドルウェア（プロダクション環境のみ）
app.add_middleware(HTTPSRedirectMiddleware)

# セッション管理のミドルウェア
secret_key = settings.SECRET_KEY
if not secret_key:
    raise ValueError("SECRET_KEY must be set")

app.add_middleware(SessionMiddleware, secret_key=secret_key)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
    expose_headers=["content-disposition"],
)

# 静的ファイルの配信設定
app.mount("/static", StaticFiles(directory="app/static"), name="static")
app.mount("/assets", StaticFiles(directory="app/static/dist/assets"), name="assets")

# テンプレートエンジンの設定
templates = Jinja2Templates(directory="app/templates")

# Inertia設定
inertia_config = InertiaConfig(
    templates=templates,
    version="1.0.0",
    root_template_filename="inertia.html",
    environment="development" if settings.ENV == EnvEnum.LOCAL.value else "production",
    dev_url="http://localhost:5173",
    root_directory="src",
    entrypoint_filename="main.tsx",
    manifest_json_path="app/static/dist/.vite/manifest.json",
)

inertia_dependency = inertia_dependency_factory(inertia_config)
InertiaDep = Annotated[Inertia, Depends(inertia_dependency)]


@app.get("/favicon.ico", include_in_schema=False)
async def favicon():
    """
    Favicon
    """
    return FileResponse("app/static/favicon.svg", media_type="image/svg+xml")


@app.get("/healthcheck")
async def healthcheck():
    try:
        return {
            "status": "OK",
            "timestamp": datetime.now().isoformat(),
            "version": "1.0.0",
        }
    except Exception as e:
        logger.error(f"Health check failed. {{ {e} }}")
        raise HTTPException(status_code=503, detail="Service Unavailable")


app.include_router(api_v1_router, prefix="/api/v1")
app.include_router(web_router)


@app.exception_handler(BadRequestException)
def bad_request_exception_handler(
    _request: Request,
    exc: BadRequestException,
):
    # error_codeを整数に変換
    error_code = exc.error_code
    if isinstance(error_code, str):
        try:
            error_code = int(error_code)
        except ValueError:
            error_code = 400

    return BadRequestResponse(
        message=exc.message,
        error_code=error_code,
        errors=None,  # 型の不整合を避けるため、一旦Noneに設定
    )


@app.exception_handler(UnauthorizedException)
def unauthorized_exception_handler(
    _request: Request,
    exc: UnauthorizedException,
):
    return UnauthorizedResponse(exc.message)


@app.exception_handler(AccessDeniedException)
def access_denied_exception_handler(
    _request: Request,
    exc: UnauthorizedException,
):
    return AccessDeniedResponse(exc.message)


@app.exception_handler(ServerErrorException)
def server_error_handler(
    _request: Request,
    exc: ServerErrorException,
):
    return ServerErrorResponse(exc.message)


@app.exception_handler(ValueError)
async def value_error_exception_handler(
    _request: Request,
    exc: ValueError,
):
    return BadRequestResponse(str(exc))


@app.exception_handler(Exception)
async def generic_exception_handler(
    _request: Request,
    exc: Exception,
):
    return ServerErrorResponse(str(exc))


@app.exception_handler(ImportErrorException)
def import_error_handler(
    _request: Request,
    exc: ImportErrorException,
):
    return ImportErrorResponse(exc.message)


@app.exception_handler(HTTPNotFoundException)
def not_found_error_handler(
    _request: Request,
    exc: HTTPNotFoundException,
):
    return NotFoundErrorResponse(exc.message)


@app.middleware("http")
async def log_cors_errors(
    request: Request,
    call_next: Callable[[Request], Awaitable[Response]],
) -> Response:
    """
    CORSエラーハンドラ

    - CORSエラーが発生した場合にログを出力します。

    :param request: リクエストデータ
    :param call_next: 次のミドルウェアを呼び出す関数
    :return: レスポンスデータ
    """

    response = await call_next(request)
    # エラーログを出力する
    if (
        response.status_code == 403
        and request.method == "OPTIONS"
        and "preflight" in str(request.url)
    ):
        timestamp = datetime.now().isoformat()
        client_ip = request.client.host if request.client else "Unknown"
        method = request.method
        host = request.headers.get("Host", "No Host")
        origin = request.headers.get("Origin", "No Origin")
        referer = request.headers.get("Referer", "No Referer")
        user_agent = request.headers.get("User-Agent", "No User-Agent")
        error_message = (
            f"[{timestamp}] Access forbidden for {request.url} - "
            f"Method: [{method}], Client IP: [{client_ip}], Host: [{host}], Origin: [{origin}], Referer: [{referer}], User-Agent: [{user_agent}]. - "
            "This may be due to CORS policy restrictions."
        )
        logger.error(error_message)

    return response


def _is_api_request(request: Request) -> bool:
    """
    APIリクエストかどうかを判定する
    """

    path = request.url.path
    return (
        path.startswith("/api/")
        or path.startswith("/docs")
        or path.startswith("/redoc")
        or path.startswith("/openapi.json")
        or "application/json" in request.headers.get("accept", "")
    )


def _get_error_details(status_code: int) -> tuple[str, str, str]:
    """
    HTTPステータスコードからタイトル、メッセージ、アイコンを取得
    """
    error_details = {
        400: ("リクエストエラー", "送信されたリクエストに問題があります。", "warning"),
        401: ("認証が必要です", "このページを表示するにはログインが必要です。", "lock"),
        403: ("アクセス拒否", "このページにアクセスする権限がありません。", "block"),
        404: (
            "ページが見つかりません",
            "お探しのページは存在しないか、移動または削除された可能性があります。",
            "not-found",
        ),
        405: (
            "メソッドが許可されていません",
            "この操作は許可されていません。",
            "error",
        ),
        422: ("データエラー", "送信されたデータに問題があります。", "warning"),
        500: ("サーバーエラー", "サーバー内部でエラーが発生しました。", "warning"),
    }
    return error_details.get(
        status_code, ("システムエラー", "予期しないエラーが発生しました。", "warning")
    )


@app.exception_handler(HTTPException)
async def http_exception_handler(
    request: Request,
    exc: HTTPException,
) -> JSONResponse | HTMLResponse:
    """
    HTTPExceptionハンドラ

    - APIリクエストの場合は、JSONレスポンスを返す。
    - ウェブページリクエストの場合は、HTMLエラーページを返す。

    :param request: リクエストデータ
    :param exc: HTTPException
    :return: JSONレスポンスまたはHTMLレスポンス
    """

    # APIリクエストかウェブページリクエストかを判定
    if _is_api_request(request):
        # JSONレスポンス
        return JSONResponse(
            status_code=exc.status_code,
            content={
                "success": False,
                "error_code": f"HTTP_{exc.status_code}",
                "message": exc.detail,
                "timestamp": datetime.now().isoformat(),
            },
        )
    else:
        # HTMLエラーページ
        title, message, icon = _get_error_details(exc.status_code)
        try:
            # 現在のロケールを取得
            current_locale = get_current_locale()
            # Jinja2テンプレートを使用してHTMLを生成
            html_content = templates.get_template("error.html").render(
                title=title,
                message=message,
                icon=icon,
                error_code=f"HTTP_{exc.status_code}",
                timestamp=datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                i18n=lambda key, **kwargs: i18n.t(key, locale=current_locale, **kwargs),
            )
            return HTMLResponse(
                content=html_content,
                status_code=exc.status_code,
            )
        except Exception:
            # テンプレートエラーの場合はフォールバック
            fallback_html = f"""
            <!DOCTYPE html>
            <html>
            <head><title>{title} - FastAPI App</title></head>
            <body>
                <h1>{title}</h1>
                <p>{message}</p>
                <p><a href="/">ホームに戻る</a></p>
            </body>
            </html>
            """
            return HTMLResponse(content=fallback_html, status_code=exc.status_code)


@app.exception_handler(StarletteHTTPException)
async def starlette_http_exception_handler(
    request: Request,
    exc: StarletteHTTPException,
):
    """
    Starlette HTTPExceptionハンドラ

    - APIリクエストの場合は、JSONレスポンスを返す。
    - ウェブページリクエストの場合は、HTMLエラーページを返す。

    :param request: リクエストデータ
    :param exc: Starlette HTTPException
    :return: JSONレスポンスまたはHTMLレスポンス
    """

    # APIリクエストかウェブページリクエストかを判定
    if _is_api_request(request):
        # JSONレスポンス
        return JSONResponse(
            status_code=exc.status_code,
            content={
                "success": False,
                "error_code": f"HTTP_{exc.status_code}",
                "message": exc.detail if hasattr(exc, "detail") else str(exc),
                "timestamp": datetime.now().isoformat(),
            },
        )
    else:
        # HTMLエラーページ
        title, message, icon = _get_error_details(exc.status_code)
        try:
            # 現在のロケールを取得
            current_locale = get_current_locale()
            # Jinja2テンプレートを使用してHTMLを生成
            html_content = templates.get_template("error.html").render(
                title=title,
                message=message,
                icon=icon,
                error_code=f"HTTP_{exc.status_code}",
                timestamp=datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                i18n=lambda key, **kwargs: i18n.t(key, locale=current_locale, **kwargs),
            )
            return HTMLResponse(
                content=html_content,
                status_code=exc.status_code,
            )
        except Exception:
            # テンプレートエラーの場合はフォールバック
            fallback_html = f"""
            <!DOCTYPE html>
            <html>
            <head><title>{title} - FastAPI App</title></head>
            <body>
                <h1>{title}</h1>
                <p>{message}</p>
                <p><a href="/">ホームに戻る</a></p>
            </body>
            </html>
            """
            return HTMLResponse(
                content=fallback_html,
                status_code=exc.status_code,
            )


# バリデーション例外ハンドラーを登録
app.exception_handler(RequestValidationError)(validation_exception_handler)


# SQLAlchemyのログ出力設定
if settings.IS_SQL_LOGGING:
    logging.getLogger("sqlalchemy.engine").setLevel(logging.INFO)


# ヘルスチェック用エンドポイントへのアクセスをログから除外する
logging.getLogger("uvicorn.access").addFilter(
    lambda record: "GET /healthcheck HTTP/1.1" not in record.getMessage()
)
