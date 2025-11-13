# coding: utf-8

from typing import Dict, List  # noqa: F401
import importlib
import pkgutil

from openapi_server.apis.default_api_base import BaseDefaultApi
import openapi_server.impl

from fastapi import (  # noqa: F401
    APIRouter,
    Body,
    Cookie,
    Depends,
    Form,
    Header,
    HTTPException,
    Path,
    Query,
    Response,
    Security,
    status,
)

from openapi_server.models.extra_models import TokenModel  # noqa: F401
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

router = APIRouter()

ns_pkg = openapi_server.impl
for _, name, _ in pkgutil.iter_modules(ns_pkg.__path__, ns_pkg.__name__ + "."):
    importlib.import_module(name)


@router.delete(
    "/orders/{id}",
    responses={
        200: {"description": "OK"},
        404: {"description": "Not Found"},
    },
    tags=["default"],
    summary="Cancel order (owner only)",
    response_model_by_alias=True,
)
async def orders_id_delete(
    id: int = Path(..., description=""),
    token_bearerAuth: TokenModel = Security(
        get_token_bearerAuth
    ),
) -> None:
    if not BaseDefaultApi.subclasses:
        raise HTTPException(status_code=500, detail="Not implemented")
    return await BaseDefaultApi.subclasses[0]().orders_id_delete(id)


@router.get(
    "/orders/{id}",
    responses={
        200: {"model": Order, "description": "OK"},
        404: {"description": "Not Found"},
    },
    tags=["default"],
    summary="Get order by id (owner only)",
    response_model_by_alias=True,
)
async def orders_id_get(
    id: int = Path(..., description=""),
    token_bearerAuth: TokenModel = Security(
        get_token_bearerAuth
    ),
) -> Order:
    if not BaseDefaultApi.subclasses:
        raise HTTPException(status_code=500, detail="Not implemented")
    return await BaseDefaultApi.subclasses[0]().orders_id_get(id)


@router.post(
    "/orders",
    responses={
        201: {"model": Order, "description": "Created"},
        400: {"description": "Bad Request"},
    },
    tags=["default"],
    summary="Place order (&lt;&#x3D;3 items)",
    response_model_by_alias=True,
)
async def orders_post(
    place_order_req: PlaceOrderReq = Body(None, description=""),
    token_bearerAuth: TokenModel = Security(
        get_token_bearerAuth
    ),
) -> Order:
    if not BaseDefaultApi.subclasses:
        raise HTTPException(status_code=500, detail="Not implemented")
    return await BaseDefaultApi.subclasses[0]().orders_post(place_order_req)


@router.get(
    "/products",
    responses={
        200: {"model": List[Product], "description": "OK"},
    },
    tags=["default"],
    summary="List products",
    response_model_by_alias=True,
)
async def products_get(
) -> List[Product]:
    if not BaseDefaultApi.subclasses:
        raise HTTPException(status_code=500, detail="Not implemented")
    return await BaseDefaultApi.subclasses[0]().products_get()


@router.get(
    "/products/{id}",
    responses={
        200: {"model": Product, "description": "OK"},
        404: {"description": "Not Found"},
    },
    tags=["default"],
    summary="Get product",
    response_model_by_alias=True,
)
async def products_id_get(
    id: int = Path(..., description=""),
) -> Product:
    if not BaseDefaultApi.subclasses:
        raise HTTPException(status_code=500, detail="Not implemented")
    return await BaseDefaultApi.subclasses[0]().products_id_get(id)


@router.get(
    "/",
    responses={
        200: {"model": Greeting, "description": "OK"},
    },
    tags=["default"],
    summary="Greeting",
    response_model_by_alias=True,
)
async def root_get(
) -> Greeting:
    if not BaseDefaultApi.subclasses:
        raise HTTPException(status_code=500, detail="Not implemented")
    return await BaseDefaultApi.subclasses[0]().root_get()


@router.post(
    "/users/deactivate",
    responses={
        200: {"description": "OK"},
    },
    tags=["default"],
    summary="Deactivate my account",
    response_model_by_alias=True,
)
async def users_deactivate_post(
    token_bearerAuth: TokenModel = Security(
        get_token_bearerAuth
    ),
) -> None:
    if not BaseDefaultApi.subclasses:
        raise HTTPException(status_code=500, detail="Not implemented")
    return await BaseDefaultApi.subclasses[0]().users_deactivate_post()


@router.post(
    "/users/login",
    responses={
        200: {"model": JWTToken, "description": "OK"},
        401: {"description": "Unauthorized"},
    },
    tags=["default"],
    summary="Login (issue JWT)",
    response_model_by_alias=True,
)
async def users_login_post(
    login_req: LoginReq = Body(None, description=""),
) -> JWTToken:
    if not BaseDefaultApi.subclasses:
        raise HTTPException(status_code=500, detail="Not implemented")
    return await BaseDefaultApi.subclasses[0]().users_login_post(login_req)


@router.get(
    "/users/me",
    responses={
        200: {"model": UserPublic, "description": "OK"},
        401: {"description": "Unauthorized"},
    },
    tags=["default"],
    summary="Get my profile",
    response_model_by_alias=True,
)
async def users_me_get(
    token_bearerAuth: TokenModel = Security(
        get_token_bearerAuth
    ),
) -> UserPublic:
    if not BaseDefaultApi.subclasses:
        raise HTTPException(status_code=500, detail="Not implemented")
    return await BaseDefaultApi.subclasses[0]().users_me_get()


@router.patch(
    "/users/me",
    responses={
        200: {"model": UserPublic, "description": "OK"},
    },
    tags=["default"],
    summary="Update my profile",
    response_model_by_alias=True,
)
async def users_me_patch(
    update_user_req: UpdateUserReq = Body(None, description=""),
    token_bearerAuth: TokenModel = Security(
        get_token_bearerAuth
    ),
) -> UserPublic:
    if not BaseDefaultApi.subclasses:
        raise HTTPException(status_code=500, detail="Not implemented")
    return await BaseDefaultApi.subclasses[0]().users_me_patch(update_user_req)


@router.post(
    "/users/register",
    responses={
        201: {"model": UserPublic, "description": "Created"},
    },
    tags=["default"],
    summary="Register user",
    response_model_by_alias=True,
)
async def users_register_post(
    register_user_req: RegisterUserReq = Body(None, description=""),
) -> UserPublic:
    if not BaseDefaultApi.subclasses:
        raise HTTPException(status_code=500, detail="Not implemented")
    return await BaseDefaultApi.subclasses[0]().users_register_post(register_user_req)
