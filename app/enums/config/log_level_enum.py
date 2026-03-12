import enum

__all__ = [
    "LogLevelEnum",
]


class LogLevelEnum(str, enum.Enum):
    DEBUG = "DEBUG"
    INFO = "INFO"
    WARNING = "WARNING"
    ERROR = "ERROR"
    CRITICAL = "CRITICAL"
