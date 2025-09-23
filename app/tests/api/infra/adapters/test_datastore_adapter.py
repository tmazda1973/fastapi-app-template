from unittest.mock import MagicMock, patch

import pytest
from sqlalchemy.orm.query import Query
from sqlalchemy.orm.session import Session

from app.api.infra.adapters import DatastoreAdapter


@pytest.fixture
def mock_session():
    return MagicMock(spec=Session)


@pytest.fixture
def adapter(mock_session) -> DatastoreAdapter:
    return DatastoreAdapter(db_session=mock_session)


def test_add_success_case1(
    adapter,
    mock_session,
) -> None:
    """
    モデルをデータベースに追加します。

    - 正常系-ケース1

    :param adapter: アダプター
    :param mock_session: DBセッション
    :return: None
    """

    # モックを設定する
    mock_model = MagicMock()

    # テスト対象を実行する
    adapter.add(mock_model)

    # 実行結果を検証する
    mock_session.add.assert_called_once_with(mock_model)


@patch("app.api.infra.adapters.datastore_adapter.soft_delete_")
def test_soft_delete_success_case1(
    mock_func_soft_delete,
    adapter,
    mock_session,
) -> None:
    """
    モデルを論理削除します。

    - 正常系-ケース1

    :param mock_func_soft_delete: モック関数
    :param adapter: アダプター
    :param mock_session: DBセッション
    :return: None
    """

    # モックを設定する
    mock_model = MagicMock()
    mock_model.id = 123
    mock_model_class = MagicMock()
    mock_model.__class__ = mock_model_class
    mock_func_soft_delete.return_value = 1

    # テスト対象を実行する
    result = adapter.soft_delete(mock_model)

    # 実行結果を検証する
    assert result == 1
    mock_func_soft_delete.assert_called_once_with(
        db_session=mock_session,
        model_clazz=mock_model_class,
        conditions={"id": 123},
    )


def test_transaction_success_case1(
    adapter,
    mock_session,
) -> None:
    """
    トランザクションコンテキストを提供します。

    - 正常系-ケース1

    :param adapter: アダプター
    :param mock_session: DBセッション
    :return: None
    """

    with adapter.transaction():
        pass

    mock_session.commit.assert_called_once()
    mock_session.rollback.assert_not_called()


def test_transaction_failure_case1(
    adapter,
    mock_session,
) -> None:
    """
    トランザクションコンテキストを提供します。

    - 異常系-ケース1

    :param adapter: アダプター
    :param mock_session: DBセッション
    :return: None
    """

    # モックを設定する
    mock_session.in_transaction.return_value = False

    # テスト対象を実行する
    with pytest.raises(Exception):
        with adapter.transaction():
            raise Exception("Test Error")

    # 実行結果を検証する
    mock_session.commit.assert_not_called()
    mock_session.rollback.assert_called_once()


def test_paginate_success_case1_first_page(
    adapter,
) -> None:
    """
    ページネーションを実行します。

    - 正常系-ケース1-最初のページ

    :param adapter: アダプター
    :return: None
    """

    # モックを設定する
    mock_query = MagicMock(spec=Query)
    mock_query.count.return_value = 25

    mock_limited_query = MagicMock()
    mock_offset_query = MagicMock()
    mock_query.limit.return_value = mock_limited_query
    mock_limited_query.offset.return_value = mock_offset_query

    models = [MagicMock(id=1)]
    mock_offset_query.all.return_value = models

    # テスト対象を実行する
    items, total, total_pages = adapter.paginate(
        mock_query,
        page=1,
        per_page=20,
    )

    # 実行結果を検証する
    mock_limited_query.offset.assert_called_once_with(0)  # (1-1) * 20
    assert total_pages == 2  # (25 + 20 - 1) // 20 = 2


def test_paginate_success_case2_last_page(
    adapter,
) -> None:
    """
    ページネーションを実行します。

    - 正常系-ケース2-最後のページ

    :param adapter: アダプター
    :return: None
    """

    # モックを設定する
    mock_query = MagicMock(spec=Query)
    mock_query.count.return_value = 23

    mock_limited_query = MagicMock()
    mock_offset_query = MagicMock()
    mock_query.limit.return_value = mock_limited_query
    mock_limited_query.offset.return_value = mock_offset_query
    models = [
        MagicMock(id=1),
        MagicMock(id=2),
        MagicMock(id=3),
    ]
    mock_offset_query.all.return_value = models

    # テスト対象を実行する
    items, total, total_pages = adapter.paginate(
        mock_query,
        page=1,
        per_page=10,
    )

    # 実行結果を検証する
    assert total_pages == 3  # (23 + 10 - 1) // 10 = 3
