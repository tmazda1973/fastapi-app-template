from fastapi import status
from fastapi.responses import JSONResponse

from app.schemas import (
    APIErrorResponse,
    ValidationError,
)

public_api_responses = {
    400: {"model": APIErrorResponse},
    401: {"model": APIErrorResponse},
    403: {"model": APIErrorResponse},
    404: {"model": APIErrorResponse},
    500: {"model": APIErrorResponse},
    480: {"model": APIErrorResponse},
}


authenticated_api_responses = {
    400: {"model": APIErrorResponse},
    401: {"model": APIErrorResponse},
    403: {"model": APIErrorResponse},
    404: {"model": APIErrorResponse},
    500: {"model": APIErrorResponse},
    480: {"model": APIErrorResponse},
}


class BadRequestResponse(JSONResponse):
    def __init__(
        self,
        message=None,
        error_code=status.HTTP_400_BAD_REQUEST,
        errors: list[ValidationError] | None = None,
    ):
        custom_content = {
            "error_code": error_code,
            "message": message,
            "errors": errors,
        }
        super().__init__(
            status_code=status.HTTP_400_BAD_REQUEST,
            content=custom_content,
        )


class UnauthorizedResponse(JSONResponse):
    def __init__(self, message=None):
        custom_content = {
            "error_code": status.HTTP_401_UNAUTHORIZED,
            "message": message,
        }
        super().__init__(
            status_code=status.HTTP_401_UNAUTHORIZED,
            content=custom_content,
        )


class AccessDeniedResponse(JSONResponse):
    def __init__(self, message=None):
        custom_content = {
            "error_code": status.HTTP_403_FORBIDDEN,
            "message": message,
        }
        super().__init__(
            status_code=status.HTTP_403_FORBIDDEN,
            content=custom_content,
        )


class ServerErrorResponse(JSONResponse):
    def __init__(self, message=None):
        custom_content = {
            "error_code": status.HTTP_500_INTERNAL_SERVER_ERROR,
            "message": message,
        }
        super().__init__(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            content=custom_content,
        )


class ImportErrorResponse(JSONResponse):
    def __init__(self, message=None):
        custom_content = {
            "error_code": 480,
            "message": message,
        }
        super().__init__(
            status_code=480,
            content=custom_content,
        )


class NotFoundErrorResponse(JSONResponse):
    def __init__(self, message=None):
        custom_content = {
            "error_code": status.HTTP_404_NOT_FOUND,
            "message": message,
        }
        super().__init__(
            status_code=status.HTTP_404_NOT_FOUND,
            content=custom_content,
        )
