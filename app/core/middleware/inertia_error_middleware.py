import json
import typing

from fastapi import Request
from starlette.middleware.base import BaseHTTPMiddleware
from starlette.responses import JSONResponse, Response, StreamingResponse


class InertiaErrorMiddleware(BaseHTTPMiddleware):
    """
    Inertiaエラーミドルウェア
    """

    async def dispatch(
        self,
        request: Request,
        call_next: typing.Callable,
    ) -> Response:
        is_inertia = request.headers.get("X-Inertia", False)
        if hasattr(request, "state"):
            request.state.inertia_component = request.headers.get(
                "X-Inertia-Current-Component"
            )

        response = await call_next(request)
        if not is_inertia:
            return response

        if hasattr(response, "status_code") and response.status_code == 422:
            response_body = None
            if isinstance(response, JSONResponse):
                response_body = json.loads(response.body)
            elif (
                isinstance(response, StreamingResponse)
                or response.__class__.__name__ == "_StreamingResponse"
            ):
                # StreamingResponseの場合
                response_chunks = []
                async for chunk in response.body_iterator:
                    if isinstance(chunk, bytes):
                        response_chunks.append(chunk.decode())
                    else:
                        response_chunks.append(str(chunk))

                body_content = "".join(response_chunks)
                try:
                    response_body = json.loads(body_content)
                except json.JSONDecodeError:
                    return response

            if response_body and "detail" in response_body:
                # レスポンスボディが取得できた場合
                formatted_errors = {}
                for error in response_body["detail"]:
                    field_parts = [
                        p for p in error.get("loc", []) if p not in ["body", "query"]
                    ]
                    if field_parts:
                        field = field_parts[0]  # 最初のフィールド名を使用
                        formatted_errors[field] = error["msg"]

                # Inertia形式に変換する
                inertia_response = {
                    "component": getattr(
                        request.state, "inertia_component", "ErrorPage"
                    ),
                    "props": {"errors": formatted_errors},
                    "url": str(request.url),
                    "version": "1.0",
                }

                # 新しいレスポンスを作成する
                headers = dict(response.headers)
                headers["X-Inertia"] = "true"
                headers["Content-Type"] = "application/json"

                return JSONResponse(
                    content=inertia_response,
                    status_code=response.status_code,
                    headers=headers,
                )

        return response
