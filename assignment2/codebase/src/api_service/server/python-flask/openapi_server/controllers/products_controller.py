import os
from typing import Dict, Tuple, Union, List

import connexion
import grpc

from openapi_server.models.error_response import ErrorResponse  # 其实可以不用模型，返回 dict 也行
from openapi_server.models.product import Product               # 同上，可选
# from openapi_server import db_pb2, db_pb2_grpc
# from .. import db_pb2, db_pb2_grpc

import openapi_server
from openapi_server import db_pb2, db_pb2_grpc
from openapi_server.logging_service import logging_client

# ---------------- gRPC Stub 初始化 ----------------

_GRPC_CHANNEL = None
_DB_STUB = None

DB_SERVICE_ADDR = os.environ.get("DB_SERVICE_ADDR", "db_service:50051")


def _get_db_stub() -> db_pb2_grpc.DbServiceStub:
    """
    懒加载方式创建 gRPC channel 和 stub，避免每个请求都新建连接。
    默认连 localhost:50051，你在 Docker 里可以配环境变量改成 `db:50051` 之类。
    """
    global _GRPC_CHANNEL, _DB_STUB
    if _DB_STUB is None:
        target = os.environ.get("DB_GRPC_TARGET", "db_service:50051")
        _GRPC_CHANNEL = grpc.insecure_channel(target)
        _DB_STUB = db_pb2_grpc.DbServiceStub(_GRPC_CHANNEL)
    return _DB_STUB


# ---------------- 通用返回封装 ----------------

def _success(message: str, data, code: int = 200):
    body = {
        "message": message,
        "data": data,
        "code": code,
    }
    # connexion 一般允许 return (body, status_code)
    return body, code


def _error(message: str, code: int = 400):
    body = {
        "message": message,
        "data": None,
        "code": code,
    }
    return body, code


# ---------------- gRPC Product → HTTP dict ----------------

def _grpc_product_to_dict(p: db_pb2.Product) -> Dict:
    """
    把 gRPC 的 Product 消息转成 HTTP JSON 可序列化的字典。
    注意 created_at 是 google.protobuf.Timestamp，需要转成 ISO 字符串。
    """
    created_at = None
    if p.HasField("created_at"):
        dt = p.created_at.ToDatetime().astimezone()  # 转成本地带 tz 的 datetime
        created_at = dt.isoformat()

    return {
        "id": p.id,
        "name": p.name,
        "description": p.description,
        "category": p.category,
        "price": p.price,         # OpenAPI 里是 number(float)，直接给 float 即可
        "slogan": p.slogan,
        "stock": p.stock,
        "created_at": created_at,  # 对应 OpenAPI 里的 format: date-time
    }


# ---------------- /products GET ----------------

def products_get(
    category: str = None,
    page: int = None,
    page_size: int = None,
) -> Tuple[Dict, int]:
    """
    列出商品列表：调用 gRPC 的 ListProducts。

    OpenAPI 一般会把 query 参数注入到这里：
    - category: 可选，按类别过滤
    - page: 可选，页码，从 1 开始
    - page_size: 可选，每页条数
    """
    stub = _get_db_stub()

    # gRPC 请求参数的默认值处理（与你的 db.proto 中的字段保持一致）
    req = db_pb2.ListProductsRequest(
        category=category or "",
        page=page or 1,
        page_size=page_size or 20,
    )

    try:
        resp = stub.ListProducts(req)
    except grpc.RpcError as e:
        # gRPC 调用失败，返回 502
        logging_client.send_logs([{
            "service_name": "api-service/products",
            "level": "ERROR",
            "path": "/products",
            "method": "GET",
            "user_sid": "",
            "message": f"DB service error: {e.code().name} - {e.details()}"
        }])

        return _error(f"DB service error: {e.code().name} - {e.details()}", 502)

    products = [_grpc_product_to_dict(p) for p in resp.products]

    logging_client.send_logs([
        {
            "service_name": "api-service/products",
            "level": "INFO",
            "path": "/products",
            "method": "GET",
            "user_sid": "",
            "message": f"Products fetched: {len(products)}"
        }
    ])

    return _success(
        "Products fetched successfully",
        data={
            "items": products,
            "page": resp.page,
            "page_size": resp.page_size,
            "total_count": resp.total_count,
        },
        code=200,
    )


# ---------------- /products/{id} GET ----------------

def products_id_get(id_: int) -> Tuple[Dict, int]:
    """
    根据 id 返回单个商品：调用 gRPC 的 GetProduct。
    """

    stub = _get_db_stub()

    try:
        # 这里的请求消息名字要和你的 db.proto 一致：
        # 如果你在 proto 里写的是 rpc GetProduct(GetProductRequest) ...
        # 那么就用 db_pb2.GetProductRequest
        req = db_pb2.GetProductRequest(id=id_)
        p = stub.GetProduct(req)
    except grpc.RpcError as e:
        if e.code() == grpc.StatusCode.NOT_FOUND:
            logging_client.send_logs([
                {
                    "service_name": "api-service/products",
                    "level": "ERROR",
                    "path": f"/products/{id_}",
                    "method": "GET",
                    "user_sid": "",
                    "message": f"Product {id_} not found"
                }
            ])
            return _error("Product not found", 404)
        logging_client.send_logs([
            {
                "service_name": "api-service/products",
                "level": "ERROR",
                "path": f"/products/{id_}",
                "method": "GET",
                "user_sid": "",
                "message": f"DB service error: {e.code().name} - {e.details()}"
            }
        ])
        return _error(f"DB service error: {e.code().name} - {e.details()}", 502)

    logging_client.send_logs([
        {
            "service_name": "api-service/products",
            "level": "INFO",
            "path": f"/products/{id_}",
            "method": "GET",
            "user_sid": "",
            "message": f"Product {id_} fetched"
        }
    ])

    return _success(
        "Product found",
        data=_grpc_product_to_dict(p),
        code=200,
    )
