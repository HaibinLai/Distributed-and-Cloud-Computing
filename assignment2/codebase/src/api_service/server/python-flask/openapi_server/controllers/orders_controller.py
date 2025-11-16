import connexion
from typing import Dict, Tuple, Union, List

from openapi_server.models.error_response import ErrorResponse
from openapi_server.models.order import Order
from openapi_server.models.order_create_request import OrderCreateRequest

from openapi_server.logging_service import logging_client

# # ---- Fake Data Storage (for Step 1 only) ----
# FAKE_ORDERS = [
#     {
#         "id": 1,
#         "user_id": 999,
#         "product_id": 101,
#         "quantity": 2,
#         "total_price": "59.98",
#         "created_at": "2024-01-15T10:30:00Z",
#     },
#     {
#         "id": 2,
#         "user_id": 999,
#         "product_id": 102,
#         "quantity": 1,
#         "total_price": "29.99",
#         "created_at": "2024-01-20T12:00:00Z",
#     }
# ]
# # ---------------------------------------------





# def orders_get():
#     """List all orders of current user (FAKE)."""

#     # 这里暂时不验证 JWT，因为只是 fake 版本
#     return _success(
#         "Orders fetched successfully",
#         data=FAKE_ORDERS,
#         code=200
#     )


# def orders_id_delete(id):
#     """Cancel an order by id (FAKE)."""

#     global FAKE_ORDERS
#     for o in FAKE_ORDERS:
#         if o["id"] == id:
#             FAKE_ORDERS = [x for x in FAKE_ORDERS if x["id"] != id]
#             return _success(f"Order {id} cancelled successfully", None, 200)

#     return _error("Order not found", 404)


# def orders_id_get(id):
#     """Get a single order by id (FAKE)."""

#     for o in FAKE_ORDERS:
#         if o["id"] == id:
#             return _success("Order found", o, 200)

#     return _error("Order not found", 404)


# def orders_post(order_create_request):
#     """Create a new fake order."""

#     if connexion.request.is_json:
#         order_create_request = OrderCreateRequest.from_dict(
#             connexion.request.get_json()
#         )

#     new_id = max(o["id"] for o in FAKE_ORDERS) + 1

#     fake_order = {
#         "id": new_id,
#         "user_id": 999,  # 假用户
#         "product_id": order_create_request.product_id,
#         "quantity": order_create_request.quantity,
#         "total_price": f"{29.99 * order_create_request.quantity:.2f}",
#         "created_at": "2024-01-22T18:00:00Z",
#     }

#     FAKE_ORDERS.append(fake_order)

#     return _success("Order created successfully", fake_order, 201)

import connexion
from openapi_server.models.order import Order
from openapi_server.models.order_create_request import OrderCreateRequest
from openapi_server.models.error_response import ErrorResponse

from openapi_server.controllers.users_controller import _get_current_user_payload

from google.protobuf.timestamp_pb2 import Timestamp

import grpc
from openapi_server import db_pb2, db_pb2_grpc
import os


# ===== JWT 配置 =====

JWT_SECRET = os.environ.get("JWT_SECRET", "dev-secret")  # 作业环境可以简单一点
JWT_ALGO = "HS256"
JWT_EXPIRE_HOURS = 12

# ===== gRPC Stub（懒加载，全局复用 Channel）=====

_GRPC_CHANNEL = None
_DB_STUB = None


# ---------------- 通用返回封装 ----------------

def _success(message: str, data, code: int = 200):
    body = {
        "message": message,
        "data": data,
        "code": code,
    }
    logging_client.send_logs([{
        "service_name": "api-service/orders",
        "level": "INFO",
        "path": connexion.request.path,
        "method": connexion.request.method,
        "user_sid": "",
        "message": message
    }])
    # connexion 一般允许 return (body, status_code)
    return body, code


def _error(message: str, code: int = 400):
    body = {
        "message": message,
        "data": None,
        "code": code,
    }
    return body, code


def _get_db_stub() -> db_pb2_grpc.DbServiceStub:
    """
    懒加载方式创建 gRPC channel 和 stub，避免每个请求都新建连接。
    默认连 localhost:50051，你在 Docker 里可以配环境变量改成 `db:50051` 之类。
    """
    global _GRPC_CHANNEL, _DB_STUB
    if _DB_STUB is None:
        # 如果裸机，就local host:50051；如果在 Docker 里跑，就 db_service:50051
        target = os.environ.get("DB_GRPC_TARGET", "db_service:50051")
        _GRPC_CHANNEL = grpc.insecure_channel(target)
        _DB_STUB = db_pb2_grpc.DbServiceStub(_GRPC_CHANNEL)
    return _DB_STUB


def orders_get(page: int = None, page_size: int = None):
    """
    GET /orders
    - Get user_id from JWT token
    - Take gRPC ListOrdersByUser
    """
    payload, err = _get_current_user_payload()
    if err is not None:
        return err

    user_id = payload.get("user_id")
    if user_id is None:
        logging_client.send_logs([{
            "service_name": "api-service/orders",
            "level": "ERROR",
            "path": connexion.request.path,
            "method": connexion.request.method,
            "user_sid": "",
            "message": "Invalid token: missing user_id"
        }])
        return _error("Invalid token: missing user_id", 401)

    stub = _get_db_stub()

    req = db_pb2.ListOrdersByUserRequest(
        user_id=user_id,
        page=page or 1,
        page_size=page_size or 20,
    )

    try:
        resp = stub.ListOrdersByUser(req)
    except grpc.RpcError as e:
        logging_client.send_logs([{
            "service_name": "api-service/orders",
            "level": "ERROR",
            "path": connexion.request.path,
            "method": connexion.request.method,
            "user_sid": "",
            "message": f"DB service error: {e.code().name} - {e.details()}"
        }])
        return _error(f"DB service error: {e.code().name} - {e.details()}", 502)

    orders = [_grpc_order_to_dict(o) for o in resp.orders]

    logging_client.send_logs([{
        "service_name": "api-service/orders",
        "level": "INFO",
        "path": connexion.request.path,
        "method": connexion.request.method,
        "user_sid": "",
        "message": f"Fetched {len(orders)} orders for user {user_id}"
    }])
    return _success(
        "Orders fetched successfully",
        data={
            "items": orders,
            "page": resp.page,
            "page_size": resp.page_size,
            "total_count": resp.total_count,
        },
        code=200,
    )


def orders_id_get(id_, token_info=None):
    """Get a single order by id."""

    payload, err = _get_current_user_payload()
    if err is not None:
        return err 

    user_id = payload.get("user_id")
    if user_id is None:
        logging_client.send_logs([{
            "service_name": "api-service/orders",
            "level": "ERROR",
            "path": connexion.request.path,
            "method": connexion.request.method,
            "user_sid": "",
            "message": "Invalid token: missing user_id"
        }])
        return _error("Invalid token: missing user_id", 401)

    order_id = id_  # 为了可读性，内部你可以用 order_id 这个名字

    stub = _get_db_stub()
    try:
        req = db_pb2.GetOrderRequest(id=order_id)
        order_msg = stub.GetOrder(req)

        return _success("Order fetched", order_to_dict(order_msg), 200)

    except grpc.RpcError as e:
        if e.code() == grpc.StatusCode.NOT_FOUND:
            logging_client.send_logs([{
                "service_name": "api-service/orders",
                "level": "WARNING",
                "path": connexion.request.path,
                "method": connexion.request.method,
                "user_sid": "",
                "message": "Order not found"
            }])
            return _error("Order not found", 404)

        logging_client.send_logs([{
            "service_name": "api-service/orders",
            "level": "ERROR",
            "path": connexion.request.path,
            "method": connexion.request.method,
            "user_sid": "",
            "message": f"DB service error: {e.code().name} - {e.details()}"
        }])
        return _error(
            f"DB service error: {e.code().name} - {e.details()}",
            502,
        )



def orders_id_delete(id_, token_info=None):
    """
    DELETE /orders/{id}
    取消订单：DB Service 会删除订单并把库存加回去。
    """
    stub = _get_db_stub()

    # 如果要做“只能删自己的订单”的权限控制，可以先 GetOrder 看 user_id 是否等于 token_info["user_id"]

    try:
        req = db_pb2.DeleteOrderRequest(id=id_)
        # DeleteOrder 一般返回 google.protobuf.Empty，不用关心 resp 内容
        stub.DeleteOrder(req)

    except grpc.RpcError as e:
        if e.code() == grpc.StatusCode.NOT_FOUND:
            logging_client.send_logs([{
                "service_name": "api-service/orders",
                "level": "WARNING",
                "path": connexion.request.path,
                "method": connexion.request.method,
                "user_sid": "",
                "message": "Order not found"
            }])

            return _error("Order not found", 404)
        logging_client.send_logs([{
            "service_name": "api-service/orders",
            "level": "ERROR",
            "path": connexion.request.path,
            "method": connexion.request.method,
            "user_sid": "",
            "message": f"DB service error: {e.code().name} - {e.details()}"
        }])
        return _error(f"DB service error: {e.code().name} - {e.details()}", 502)

    # 调用成功就认为删除成功
    return _success("Order deleted", None, 200)



from openapi_server.models.order_create_request import OrderCreateRequest

def orders_post(order_create_request=None, token_info=None):
    """Create a new order."""

    # 兼容：如果 Connexion 没有传 order_create_request，就自己从 request.json 里解析
    if order_create_request is None and connexion.request.is_json:
        order_create_request = OrderCreateRequest.from_dict(
            connexion.request.get_json()
        )

    if order_create_request is None:
        logging_client.send_logs([{
            "service_name": "api-service/orders",
            "level": "WARNING",
            "path": connexion.request.path,
            "method": connexion.request.method,
            "user_sid": "",
            "message": "Invalid order request body"
        }])
        return _error("Invalid order request body", 400)

    # 从 token_info 中取当前用户
    user_id = token_info.get("user_id") if token_info else None
    if not user_id:
        logging_client.send_logs([{
            "service_name": "api-service/orders",
            "level": "WARNING",
            "path": connexion.request.path,
            "method": connexion.request.method,
            "user_sid": "",
            "message": "Missing user_id in token"
        }])
        return _error("Missing user_id in token", 401)

    stub = _get_db_stub()
    try:
        req = db_pb2.CreateOrderRequest(
            user_id=user_id,
            product_id=order_create_request.product_id,
            quantity=order_create_request.quantity,
        )

        order_msg = stub.CreateOrder(req)

        return _success(
            "Order created successfully",
            order_to_dict(order_msg),
            201,
        )

    except grpc.RpcError as e:
        # 这里可以根据不同错误码做更细致处理，比如库存不足/非法数量等
        logging_client.send_logs([{
            "service_name": "api-service/orders",
            "level": "ERROR",
            "path": connexion.request.path,
            "method": connexion.request.method,
            "user_sid": "",
            "message": f"DB service error: {e.code().name} - {e.details()}"
        }])
        return _error(
            f"DB service error: {e.code().name} - {e.details()}",
            502,
        )


def order_to_dict(o: db_pb2.Order):
    """
    把 gRPC Order 消息转成纯 JSON 可序列化的 dict。
    确保里面只包含 int/float/str/bool/None/list/dict。
    """
    # 处理 created_at: protobuf Timestamp -> ISO 字符串
    created_at = None
    if o.HasField("created_at"):
        # ToDatetime() 返回 naive/aware 视情况，你可以再 astimezone() 一下
        dt = o.created_at.ToDatetime()
        # 如果需要本地时区可以: dt = dt.astimezone()
        created_at = dt.isoformat()

    return {
        "id": o.id,
        "user_id": o.user_id,
        "product_id": o.product_id,
        "quantity": o.quantity,
        "total_price": float(o.total_price),  # 确保是 float
        "created_at": created_at,
    }



def _grpc_order_to_dict(o: db_pb2.Order):
    created_at = None
    if o.HasField("created_at"):
        dt = o.created_at.ToDatetime().astimezone()
        created_at = dt.isoformat()

    return {
        "id": o.id,
        "user_id": o.user_id,
        "product_id": o.product_id,
        "quantity": o.quantity,
        "total_price": o.total_price,
        "created_at": created_at,
    }