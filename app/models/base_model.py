from __future__ import annotations

from datetime import datetime
from typing import Any

from sqlalchemy import BIGINT, TIMESTAMP, event, func, null
from sqlalchemy.orm import (
    ORMExecuteState,
    Session,
    declarative_mixin,
    with_loader_criteria,
)
from sqlmodel import Field, SQLModel

__all__ = [
    "BaseModel",
]


@declarative_mixin
class SoftDeleteMixin:
    """
    論理削除ミックスイン

    :var deleted_at: datetime | None: 削除日時
    """

    deleted_at: datetime | None = Field(
        default=None,
        sa_type=TIMESTAMP(timezone=True),  # type: ignore[assignment]
        sa_column_kwargs={
            "server_default": None,
        },
        nullable=True,
    )

    def soft_delete(self) -> None:
        """
        データを論理削除します。

        :return: None
        """
        self.deleted_at = func.now()

    def is_active(self) -> bool:
        """
        レコードが有効であるかを判定します。

        :return: bool: True: 有効, False: 無効
        """
        return self.deleted_at is None


class BaseModel(SQLModel, SoftDeleteMixin):
    """
    基底モデル

    :var id: int: ID
    :var created_at: datetime | None: 作成日時
    :var updated_at: datetime | None: 更新日時
    """

    __abstract__ = True

    model_config = {
        "arbitrary_types_allowed": True,
        "ignored_types": (
            # SQLAlchemyのrelationshipオブジェクトを無視
            type(None).__class__.__bases__[0],  # object型を含む基底型
        ),
    }  # SQLModelでSQLAlchemyの型定義を利用できるようにする

    id: int = Field(sa_type=BIGINT, default=None, primary_key=True)

    created_at: datetime = Field(
        default=None,
        sa_type=TIMESTAMP(timezone=True),  # type: ignore[assignment]
        sa_column_kwargs={
            "server_default": func.now(),
        },
    )
    updated_at: datetime = Field(
        default=None,
        sa_type=TIMESTAMP(timezone=True),  # type: ignore[assignment]
        sa_column_kwargs={
            "server_default": func.now(),
            "onupdate": func.now(),
        },
    )

    def update_by_dict(
        self,
        data: dict[str, Any],
    ) -> None:
        """
        辞書から属性を更新します。

        :param data: 更新する属性の辞書
        :return: None
        """

        for key in data:
            if hasattr(self, key):
                setattr(self, key, data[key])


@event.listens_for(Session, "do_orm_execute")
def _add_filtering_deleted_at(
    execute_state: ORMExecuteState,
) -> None:
    """
    論理削除用のフィルタを自動的に適用します。

    - 以下のようにすると、論理削除済のデータも含めて取得可能

    query(...).filter(...).execution_options(include_deleted=True)

    :param execute_state: SQLステートメント
    """

    if (
        execute_state.is_select
        and not execute_state.is_column_load
        and not execute_state.is_relationship_load
        and not execute_state.execution_options.get("include_deleted", False)
    ):
        execute_state.statement = execute_state.statement.options(
            with_loader_criteria(
                SoftDeleteMixin,
                lambda cls: cls.deleted_at == null(),  # type: ignore[arg-type]
                include_aliases=True,
            )
        )
