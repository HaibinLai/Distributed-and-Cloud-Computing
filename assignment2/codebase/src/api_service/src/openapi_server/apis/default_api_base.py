# coding: utf-8

from typing import ClassVar, Dict, List, Tuple  # noqa: F401

from openapi_server.models.greeting import Greeting
from openapi_server.models.jwt_token import JWTToken
from openapi_server.models.login_req import LoginReq
from openapi_server.models.order import Order
from openapi_server.models.place_order_req import PlaceOrderReq
from openapi_server.models.product import Product
from openapi_server.models.register_user_req import RegisterUserReq
from openapi_server.models.update_user_req import UpdateUserReq
from openapi_server.models.user_public import UserPublic
from openapi_server.security_api import get_token_bearerAuth

class BaseDefaultApi:
    subclasses: ClassVar[Tuple] = ()

    def __init_subclass__(cls, **kwargs):
        super().__init_subclass__(**kwargs)
        BaseDefaultApi.subclasses = BaseDefaultApi.subclasses + (cls,)
    async def orders_id_delete(
        self,
        id: int,
    ) -> None:
        ...


    async def orders_id_get(
        self,
        id: int,
    ) -> Order:
        ...


    async def orders_post(
        self,
        place_order_req: PlaceOrderReq,
    ) -> Order:
        ...


    async def products_get(
        self,
    ) -> List[Product]:
        ...


    async def products_id_get(
        self,
        id: int,
    ) -> Product:
        ...


    async def root_get(
        self,
    ) -> Greeting:
        ...


    async def users_deactivate_post(
        self,
    ) -> None:
        ...


    async def users_login_post(
        self,
        login_req: LoginReq,
    ) -> JWTToken:
        ...


    async def users_me_get(
        self,
    ) -> UserPublic:
        ...


    async def users_me_patch(
        self,
        update_user_req: UpdateUserReq,
    ) -> UserPublic:
        ...


    async def users_register_post(
        self,
        register_user_req: RegisterUserReq,
    ) -> UserPublic:
        ...
