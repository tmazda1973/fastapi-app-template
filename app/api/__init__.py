from fastapi.routing import APIRoute, APIRouter

from .api_v1 import api_v1_router


# path operation関数 の名前をoperationIdとして使用する
# https://fastapi.tiangolo.com/ja/advanced/path-operation-advanced-configuration/#path-operation-operationid
def use_route_names_as_operation_ids(router: APIRouter) -> None:
    """
    Simplify operation IDs so that generated API clients have simpler function
    names.

    Should be called only after all routes have been added.
    """
    for route in router.routes:
        if isinstance(route, APIRoute):
            # operation_idが設定されていなければ、ルートの名前（関数名）を使用する
            if not route.operation_id:
                route.operation_id = route.name  # in this case, 'read_items'


use_route_names_as_operation_ids(api_v1_router)
