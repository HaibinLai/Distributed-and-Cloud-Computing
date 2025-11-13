import connexion
from typing import Dict, Tuple, Union, List

from openapi_server.models.error_response import ErrorResponse
from openapi_server.models.order import Order
from openapi_server.models.order_create_request import OrderCreateRequest


# ---- Fake Data Storage (for Step 1 only) ----
FAKE_ORDERS = [
    {
        "id": 1,
        "user_id": 999,
        "product_id": 101,
        "quantity": 2,
        "total_price": "59.98",
        "created_at": "2024-01-15T10:30:00Z",
    },
    {
        "id": 2,
        "user_id": 999,
        "product_id": 102,
        "quantity": 1,
        "total_price": "29.99",
        "created_at": "2024-01-20T12:00:00Z",
    }
]
# ---------------------------------------------


def _success(message: str, data=None, code=200):
    """Helper: success response."""
    return {
        "success": True,
        "message": message,
        "data": data
    }, code


def _error(message: str, code: int):
    """Helper: error response."""
    return {
        "success": False,
        "error": message,
        "code": code
    }, code


def orders_get():
    """List all orders of current user (FAKE)."""

    # 这里暂时不验证 JWT，因为只是 fake 版本
    return _success(
        "Orders fetched successfully",
        data=FAKE_ORDERS,
        code=200
    )


def orders_id_delete(id):
    """Cancel an order by id (FAKE)."""

    global FAKE_ORDERS
    for o in FAKE_ORDERS:
        if o["id"] == id:
            FAKE_ORDERS = [x for x in FAKE_ORDERS if x["id"] != id]
            return _success(f"Order {id} cancelled successfully", None, 200)

    return _error("Order not found", 404)


def orders_id_get(id):
    """Get a single order by id (FAKE)."""

    for o in FAKE_ORDERS:
        if o["id"] == id:
            return _success("Order found", o, 200)

    return _error("Order not found", 404)


def orders_post(order_create_request):
    """Create a new fake order."""

    if connexion.request.is_json:
        order_create_request = OrderCreateRequest.from_dict(
            connexion.request.get_json()
        )

    new_id = max(o["id"] for o in FAKE_ORDERS) + 1

    fake_order = {
        "id": new_id,
        "user_id": 999,  # 假用户
        "product_id": order_create_request.product_id,
        "quantity": order_create_request.quantity,
        "total_price": f"{29.99 * order_create_request.quantity:.2f}",
        "created_at": "2024-01-22T18:00:00Z",
    }

    FAKE_ORDERS.append(fake_order)

    return _success("Order created successfully", fake_order, 201)
