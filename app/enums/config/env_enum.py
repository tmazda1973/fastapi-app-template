import enum

__all__ = [
    "EnvEnum",
]


class EnvEnum(str, enum.Enum):
    LOCAL = "LOCAL"
    DEV = "DEV"
    STG = "STG"
    PROD = "PROD"
    TEST = "TEST"
