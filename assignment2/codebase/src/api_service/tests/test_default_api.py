# coding: utf-8

from fastapi.testclient import TestClient


from openapi_server.models.greeting import Greeting  # noqa: F401
from openapi_server.models.jwt_token import JWTToken  # noqa: F401
from openapi_server.models.login_req import LoginReq  # noqa: F401
from openapi_server.models.order import Order  # noqa: F401
from openapi_server.models.place_order_req import PlaceOrderReq  # noqa: F401
from openapi_server.models.product import Product  # noqa: F401
from openapi_server.models.register_user_req import RegisterUserReq  # noqa: F401
from openapi_server.models.update_user_req import UpdateUserReq  # noqa: F401
from openapi_server.models.user_public import UserPublic  # noqa: F401


def test_orders_id_delete(client: TestClient):
    """Test case for orders_id_delete

    Cancel order (owner only)
    """

    headers = {
        "Authorization": "Bearer special-key",
    }
    # uncomment below to make a request
    #response = client.request(
    #    "DELETE",
    #    "/orders/{id}".format(id=56),
    #    headers=headers,
    #)

    # uncomment below to assert the status code of the HTTP response
    #assert response.status_code == 200


def test_orders_id_get(client: TestClient):
    """Test case for orders_id_get

    Get order by id (owner only)
    """

    headers = {
        "Authorization": "Bearer special-key",
    }
    # uncomment below to make a request
    #response = client.request(
    #    "GET",
    #    "/orders/{id}".format(id=56),
    #    headers=headers,
    #)

    # uncomment below to assert the status code of the HTTP response
    #assert response.status_code == 200


def test_orders_post(client: TestClient):
    """Test case for orders_post

    Place order (<=3 items)
    """
    place_order_req = {"quantity":2,"product_id":0}

    headers = {
        "Authorization": "Bearer special-key",
    }
    # uncomment below to make a request
    #response = client.request(
    #    "POST",
    #    "/orders",
    #    headers=headers,
    #    json=place_order_req,
    #)

    # uncomment below to assert the status code of the HTTP response
    #assert response.status_code == 200


def test_products_get(client: TestClient):
    """Test case for products_get

    List products
    """

    headers = {
    }
    # uncomment below to make a request
    #response = client.request(
    #    "GET",
    #    "/products",
    #    headers=headers,
    #)

    # uncomment below to assert the status code of the HTTP response
    #assert response.status_code == 200


def test_products_id_get(client: TestClient):
    """Test case for products_id_get

    Get product
    """

    headers = {
    }
    # uncomment below to make a request
    #response = client.request(
    #    "GET",
    #    "/products/{id}".format(id=56),
    #    headers=headers,
    #)

    # uncomment below to assert the status code of the HTTP response
    #assert response.status_code == 200


def test_root_get(client: TestClient):
    """Test case for root_get

    Greeting
    """

    headers = {
    }
    # uncomment below to make a request
    #response = client.request(
    #    "GET",
    #    "/",
    #    headers=headers,
    #)

    # uncomment below to assert the status code of the HTTP response
    #assert response.status_code == 200


def test_users_deactivate_post(client: TestClient):
    """Test case for users_deactivate_post

    Deactivate my account
    """

    headers = {
        "Authorization": "Bearer special-key",
    }
    # uncomment below to make a request
    #response = client.request(
    #    "POST",
    #    "/users/deactivate",
    #    headers=headers,
    #)

    # uncomment below to assert the status code of the HTTP response
    #assert response.status_code == 200


def test_users_login_post(client: TestClient):
    """Test case for users_login_post

    Login (issue JWT)
    """
    login_req = {"password":"password","username":"username"}

    headers = {
    }
    # uncomment below to make a request
    #response = client.request(
    #    "POST",
    #    "/users/login",
    #    headers=headers,
    #    json=login_req,
    #)

    # uncomment below to assert the status code of the HTTP response
    #assert response.status_code == 200


def test_users_me_get(client: TestClient):
    """Test case for users_me_get

    Get my profile
    """

    headers = {
        "Authorization": "Bearer special-key",
    }
    # uncomment below to make a request
    #response = client.request(
    #    "GET",
    #    "/users/me",
    #    headers=headers,
    #)

    # uncomment below to assert the status code of the HTTP response
    #assert response.status_code == 200


def test_users_me_patch(client: TestClient):
    """Test case for users_me_patch

    Update my profile
    """
    update_user_req = {"username":"username"}

    headers = {
        "Authorization": "Bearer special-key",
    }
    # uncomment below to make a request
    #response = client.request(
    #    "PATCH",
    #    "/users/me",
    #    headers=headers,
    #    json=update_user_req,
    #)

    # uncomment below to assert the status code of the HTTP response
    #assert response.status_code == 200


def test_users_register_post(client: TestClient):
    """Test case for users_register_post

    Register user
    """
    register_user_req = {"password":"password","username":"username"}

    headers = {
    }
    # uncomment below to make a request
    #response = client.request(
    #    "POST",
    #    "/users/register",
    #    headers=headers,
    #    json=register_user_req,
    #)

    # uncomment below to assert the status code of the HTTP response
    #assert response.status_code == 200

