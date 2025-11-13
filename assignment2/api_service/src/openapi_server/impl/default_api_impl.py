from typing import List
from fastapi import HTTPException
from openapi_server.apis.default_api_base import BaseDefaultApi
# from openapi_server.models import (
#     Greeting, Product, Order, PlaceOrderReq,
#     UserPublic, RegisterUserReq, LoginReq, JWTToken, UpdateUserReq
# )

from openapi_server.models.greeting import Greeting
from openapi_server.models.product import Product
from openapi_server.models.order import Order
from openapi_server.models.place_order_req import PlaceOrderReq
from openapi_server.models.user_public import UserPublic
from openapi_server.models.register_user_req import RegisterUserReq
from openapi_server.models.login_req import LoginReq
from openapi_server.models.jwt_token import JWTToken
from openapi_server.models.update_user_req import UpdateUserReq

class DefaultApiImpl(BaseDefaultApi):
    async def root_get(self) -> Greeting:
        return Greeting(message="Welcome!")

    async def products_get(self) -> List[Product]:
        # TODO: 换成 gRPC 调 DB
        return [Product(id=1, name="Hoodie", category="clothes", price=199.0, stock=50)]

    async def products_id_get(self, id: int) -> Product:
        if id == 1:
            return Product(id=1, name="Hoodie", category="clothes", price=199.0, stock=50)
        raise HTTPException(404, "Product not found")

    async def users_register_post(self, register_user_req: RegisterUserReq) -> UserPublic:
        return UserPublic(id=1, username=register_user_req.username, active=True)

    async def users_login_post(self, login_req: LoginReq) -> JWTToken:
        return JWTToken(access_token="fake.token", token_type="Bearer")

    async def users_me_get(self) -> UserPublic:
        return UserPublic(id=1, username="haibin", active=True)

    async def users_me_patch(self, update_user_req: UpdateUserReq) -> UserPublic:
        return UserPublic(id=1, username=update_user_req.username or "haibin", active=True)

    async def users_deactivate_post(self) -> None:
        return None

    async def orders_post(self, place_order_req: PlaceOrderReq) -> Order:
        if not (1 <= place_order_req.quantity <= 3):
            raise HTTPException(400, "Quantity must be 1..3")
        return Order(id=101, user_id=1, product_id=place_order_req.product_id,
                     quantity=place_order_req.quantity, total_price=199.0 * place_order_req.quantity,
                     status="PLACED")

    async def orders_id_get(self, id: int) -> Order:
        if id == 101:
            return Order(id=101, user_id=1, product_id=1, quantity=2, total_price=398.0, status="PLACED")
        raise HTTPException(404, "Not Found")

    async def orders_id_delete(self, id: int) -> None:
        return None
