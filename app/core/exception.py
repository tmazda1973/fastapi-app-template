from fastapi import HTTPException, status

from app.core.errors.codes import ErrorCode
from app.core.i18n import ErrorMessage
from app.schemas import ValidationError

__all__ = [
    "BadRequestException",
    "UnauthorizedException",
    "AccessDeniedException",
    "ServerErrorException",
    "ImportErrorException",
    "HTTPNotFoundException",
]


class BadRequestException(Exception):
    """
    エラークラス（400 Bad Request）
    """

    def __init__(
        self,
        error_code: str | int,
        message: str = None,
        errors: list[ValidationError] | None = None,
    ) -> None:
        self.status_code = status.HTTP_400_BAD_REQUEST
        self.error_code = error_code
        self.message = message
        self._errors = errors

    @property
    def errors(self) -> list[dict] | None:
        if self._errors is None:
            return None

        return [error.model_dump() for error in self._errors]


class UnauthorizedException(Exception):
    """
    エラークラス（401 Unauthorized）
    """

    def __init__(
        self,
        error_code: str | int,
        message: str = None,
    ) -> None:
        self.status_code = status.HTTP_401_UNAUTHORIZED
        self.error_code = error_code
        self.message = message


class HTTPNotFoundException(HTTPException):
    """
    エラークラス（404 Not Found）
    """

    def __init__(
        self,
        error_code: str | int = status.HTTP_404_NOT_FOUND,
        message: str = None,
    ) -> None:
        self.status_code = status.HTTP_404_NOT_FOUND
        self.error_code = error_code
        self.message = message


class AccessDeniedException(Exception):
    """
    エラークラス（403 Forbidden）
    """

    def __init__(
        self,
        error_code: str | int,
        message: str = None,
    ) -> None:
        self.status_code = status.HTTP_403_FORBIDDEN
        self.error_code = error_code
        self.message = message


class ServerErrorException(Exception):
    """
    エラークラス（500 Internal Server Error）
    """

    def __init__(
        self,
        error_code: str | int = ErrorCode.INTERNAL_SERVER_ERROR,
        message: str = ErrorMessage(ErrorCode.INTERNAL_SERVER_ERROR).value,
    ) -> None:
        self.status_code = status.HTTP_500_INTERNAL_SERVER_ERROR
        self.error_code = error_code
        self.message = message


class ImportErrorException(Exception):
    """
    エラークラス（480 Import Error）
    """

    def __init__(
        self,
        error_code: str | int = 480,
        message: str = None,
    ) -> None:
        self.status_code = 480
        self.error_code = error_code
        self.message = message
