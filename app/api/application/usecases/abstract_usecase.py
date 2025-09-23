from abc import ABC, abstractmethod
from typing import Generic, TypeVar

__all__ = [
    "AbstractUsecase",
]

T = TypeVar("T")  # プレゼンター


class AbstractUsecase(ABC, Generic[T]):
    """
    ユースケース抽象クラス

    - T: プレゼンター
    - ユースケースは、このクラスを継承してください。
    """

    @abstractmethod
    def execute(self, presenter: T) -> None:
        """
        ユースケースを実行します。

        :return: None
        """
        pass
