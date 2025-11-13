import connexion
from typing import Dict, Tuple, Union, List

from openapi_server.models.error_response import ErrorResponse
from openapi_server.models.product import Product


# ---- Fake Product List (Step 1 only) ----
FAKE_PRODUCTS = [
    {
        "id": 101,
        "name": "SUSTech T-Shirt",
        "description": "Comfortable cotton T-shirt with SUSTech logo",
        "category": "Clothing",
        "price": "29.99",
        "slogan": "Wear Your Pride",
        "stock": 120,
        "created_at": "2024-01-10T12:00:00Z"
    },
    {
        "id": 102,
        "name": "SUSTech Hoodie",
        "description": "Warm hoodie for winter",
        "category": "Clothing",
        "price": "59.99",
        "slogan": "Soft and Warm",
        "stock": 50,
        "created_at": "2024-01-12T15:00:00Z"
    },
    {
        "id": 103,
        "name": "SUSTech Mug",
        "description": "Ceramic mug with printed logo",
        "category": "Accessories",
        "price": "14.99",
        "slogan": "Start Your Day Right",
        "stock": 200,
        "created_at": "2024-01-08T09:30:00Z"
    }
]
# -----------------------------------------


def _success(message: str, data=None, code=200):
    return {
        "success": True,
        "message": message,
        "data": data
    }, code


def _error(message: str, code: int):
    return {
        "success": False,
        "error": message,
        "code": code
    }, code


def products_get():
    """Return all products (FAKE)."""

    return _success(
        "Products fetched successfully",
        data=FAKE_PRODUCTS,
        code=200
    )


def products_id_get(id_):
    """Return product by id (FAKE)."""

    for p in FAKE_PRODUCTS:
        if p["id"] == id_:
            return _success("Product found", p, 200)

    return _error("Product not found", 404)
