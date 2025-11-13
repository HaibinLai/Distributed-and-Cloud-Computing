import connexion
from typing import Dict, Tuple, Union

from openapi_server.models.auth_token_response import AuthTokenResponse  # noqa: E501
from openapi_server.models.error_response import ErrorResponse  # noqa: E501
from openapi_server.models.user_login_request import UserLoginRequest  # noqa: E501
from openapi_server.models.user_profile import UserProfile  # noqa: E501
from openapi_server.models.user_register_request import UserRegisterRequest  # noqa: E501
from openapi_server.models.user_update_request import UserUpdateRequest  # noqa: E501
from openapi_server import util

from datetime import datetime, timezone

# ===== In-memory Fake "DB" for Step 1 =====

# USERS = {}  # key: sid, value: dict with user info + password
# NEXT_USER_ID = 1
# CURRENT_SID = None  # fake "logged-in" user sid


# def _now_iso():
#     return datetime.now(timezone.utc).isoformat().replace("+00:00", "Z")


# def _success(message: str, data=None, code=200):
#     return {
#         "success": True,
#         "message": message,
#         "data": data
#     }, code


# def _error(message: str, code: int):
#     return {
#         "success": False,
#         "error": message,
#         "code": code
#     }, code


# def _user_public_view(user_dict):
#     """Strip password, only return fields给前端。"""
#     if user_dict is None:
#         return None
#     return {
#         "id": user_dict["id"],
#         "sid": user_dict["sid"],
#         "username": user_dict.get("username"),
#         "email": user_dict.get("email"),
#         "created_at": user_dict["created_at"],
#         "is_active": user_dict["is_active"],
#     }


# ===== Controller Implementations =====


# def users_login_post(user_login_request=None):  # noqa: E501
#     """Login and get JWT (FAKE)."""

#     global CURRENT_SID

#     if connexion.request.is_json:
#         user_login_request = UserLoginRequest.from_dict(
#             connexion.request.get_json()
#         )

#     sid = user_login_request.sid
#     password = user_login_request.password

#     user = USERS.get(sid)
#     if user is None or not user["is_active"]:
#         return _error("User not found or deactivated", 401)

#     if user["password"] != password:
#         return _error("Invalid credentials", 401)

#     CURRENT_SID = sid

#     fake_token = f"fake-jwt-token-for-{sid}"

#     # data 里放 user + token，后面可以直接替换成真实 JWT
#     data = {
#         "user": _user_public_view(user),
#         "token": fake_token
#     }
#     return _success("Login successful", data, 200)


# def users_me_delete():  # noqa: E501
#     """Deactivate current user's account (FAKE)."""

#     global CURRENT_SID

#     if CURRENT_SID is None or CURRENT_SID not in USERS:
#         return _error("Not logged in", 401)

#     user = USERS[CURRENT_SID]
#     user["is_active"] = False
#     CURRENT_SID = None

#     return _success("User deactivated successfully", None, 200)


# def users_me_get():  # noqa: E501
#     """Get current user's profile (FAKE)."""

#     if CURRENT_SID is None or CURRENT_SID not in USERS:
#         return _error("Not logged in", 401)

#     user = USERS[CURRENT_SID]
#     if not user["is_active"]:
#         return _error("User is deactivated", 401)

#     return _success("Current user profile", _user_public_view(user), 200)


# def users_me_patch(user_update_request=None):  # noqa: E501
#     """Update current user's profile (FAKE)."""

#     if CURRENT_SID is None or CURRENT_SID not in USERS:
#         return _error("Not logged in", 401)

#     if connexion.request.is_json:
#         user_update_request = UserUpdateRequest.from_dict(
#             connexion.request.get_json()
#         )

#     user = USERS[CURRENT_SID]

#     # 可选字段：username / email / password
#     if user_update_request.username is not None:
#         user["username"] = user_update_request.username
#     if user_update_request.email is not None:
#         user["email"] = user_update_request.email
#     if getattr(user_update_request, "password", None) is not None:
#         user["password"] = user_update_request.password

#     return _success("User updated successfully", _user_public_view(user), 200)


# def users_register_post(user_register_request=None):  # noqa: E501
#     """Register a new user (FAKE)."""

#     global NEXT_USER_ID, CURRENT_SID

#     if connexion.request.is_json:
#         user_register_request = UserRegisterRequest.from_dict(
#             connexion.request.get_json()
#         )

#     sid = user_register_request.sid
#     password = user_register_request.password
#     username = getattr(user_register_request, "username", None)
#     email = getattr(user_register_request, "email", None)

#     if sid in USERS and USERS[sid]["is_active"]:
#         return _error("User already exists", 409)

#     created_at = _now_iso()
#     user_id = NEXT_USER_ID
#     NEXT_USER_ID += 1

#     USERS[sid] = {
#         "id": user_id,
#         "sid": sid,
#         "username": username,
#         "email": email,
#         "password": password,
#         "created_at": created_at,
#         "is_active": True,
#     }

#     CURRENT_SID = sid  # 注册后自动“登录”

#     fake_token = f"fake-jwt-token-for-{sid}"
#     data = {
#         "user": _user_public_view(USERS[sid]),
#         "token": fake_token
#     }
#     return _success("User registered successfully", data, 201)


import os
import hashlib
from typing import Dict, Tuple, Union

import connexion
import grpc
# import jwt
import jwt as pyjwt


from datetime import datetime, timezone, timedelta

from openapi_server.models.auth_token_response import AuthTokenResponse  # noqa: E501
from openapi_server.models.error_response import ErrorResponse  # noqa: E501
from openapi_server.models.user_login_request import UserLoginRequest  # noqa: E501
from openapi_server.models.user_profile import UserProfile  # noqa: E501
from openapi_server.models.user_register_request import UserRegisterRequest  # noqa: E501
from openapi_server.models.user_update_request import UserUpdateRequest  # noqa: E501
from openapi_server import util
from openapi_server import db_pb2, db_pb2_grpc

# ===== JWT 配置 =====

JWT_SECRET = os.environ.get("JWT_SECRET", "dev-secret")  # 作业环境可以简单一点
JWT_ALGO = "HS256"
JWT_EXPIRE_HOURS = 12

# ===== gRPC Stub（懒加载，全局复用 Channel）=====

_GRPC_CHANNEL = None
_DB_STUB = None


def _get_db_stub() -> db_pb2_grpc.DbServiceStub:
    global _GRPC_CHANNEL, _DB_STUB
    if _DB_STUB is None:
        target = os.environ.get("DB_GRPC_TARGET", "localhost:50051")
        _GRPC_CHANNEL = grpc.insecure_channel(target)
        _DB_STUB = db_pb2_grpc.DbServiceStub(_GRPC_CHANNEL)
    return _DB_STUB


# ===== 通用返回封装 =====

def _success(message: str, data=None, code: int = 200):
    body = {
        "message": message,
        "data": data,
        "code": code,
    }
    return body, code


def _error(message: str, code: int = 400):
    body = {
        "message": message,
        "data": None,
        "code": code,
    }
    return body, code


# ===== 工具函数：body -> dict（兼容模型 or dict）=====

def _body_to_dict(body) -> Dict:
    """
    兼容两种情况：
    1. OpenAPI Generator 传进来的是模型对象（有 .to_dict）
    2. 传进来的是原始 dict
    """
    if body is None:
        if connexion.request.is_json:
            return connexion.request.get_json()
        return {}
    if isinstance(body, dict):
        return body
    if hasattr(body, "to_dict"):
        return body.to_dict()
    # 兜底
    if connexion.request.is_json:
        return connexion.request.get_json()
    return {}


# ===== 工具函数：User(Protobuf) -> HTTP UserProfile dict =====

def _grpc_user_to_profile(u: db_pb2.User) -> Dict:
    created_at = None
    if u.HasField("created_at"):
        dt = u.created_at.ToDatetime().astimezone()
        created_at = dt.isoformat()

    return {
        "sid": u.sid,
        "username": u.username,
        "email": u.email,
        "created_at": created_at,
        "is_active": True,  # 如果你的 DB 里有 is_active 字段，可以改成 u.is_active
    }


# ===== JWT 工具函数 =====

def _create_jwt_for_user(u: db_pb2.User) -> str:
    now = datetime.now(timezone.utc)
    payload = {
        "sid": u.sid,
        "user_id": u.id,
        "iat": int(now.timestamp()),
        "exp": int((now + timedelta(hours=JWT_EXPIRE_HOURS)).timestamp()),
    }
    token = pyjwt.encode(payload, JWT_SECRET, algorithm=JWT_ALGO)
    # PyJWT>=2 默认返回 str
    return token


def _get_current_user_payload():
    """
    从 Authorization: Bearer xxx 里解析 JWT，返回 payload。
    出错直接返回 _error(...)。
    """
    auth_header = connexion.request.headers.get("Authorization", "")
    if not auth_header.startswith("Bearer "):
        return None, _error("Missing or invalid Authorization header", 401)

    token = auth_header.split(" ", 1)[1].strip()
    try:
        payload = pyjwt.decode(token, JWT_SECRET, algorithms=[JWT_ALGO])
    except pyjwt.ExpiredSignatureError:
        return None, _error("Token expired", 401)
    except pyjwt.InvalidTokenError:
        return None, _error("Invalid token", 401)

    return payload, None


# ====== Controller: register ======

def users_register_post(body: Union[UserRegisterRequest, Dict]) -> Tuple[Dict, int]:
    """
    注册接口：
    - HTTP body: {sid, username, email, password}
    - gRPC: CreateUser
    - 返回: { user: UserProfile, token: str }
    """
    stub = _get_db_stub()
    data = _body_to_dict(body)

    sid = data.get("sid")
    username = data.get("username")
    email = data.get("email", "")
    password = data.get("password")

    if not sid or not username or not password:
        return _error("sid, username and password are required", 400)

    # 简单密码 hash（作业够用，生产上应该用 bcrypt/scrypt 等）
    password_hash = hashlib.sha256(password.encode("utf-8")).hexdigest()

    try:
        req = db_pb2.CreateUserRequest(
            sid=sid,
            username=username,
            email=email,
            password_hash=password_hash,
        )
        user = stub.CreateUser(req)
    except grpc.RpcError as e:
        if e.code() == grpc.StatusCode.ALREADY_EXISTS:
            return _error(f"User already exists: {e.details()}", 409)
        return _error(f"DB service error: {e.code().name} - {e.details()}", 502)

    token = _create_jwt_for_user(user)

    resp_data = {
        "user": _grpc_user_to_profile(user),
        "token": token,
    }
    return _success("User registered successfully", resp_data, 201)


# ====== Controller: login ======

def users_login_post(body: Union[UserLoginRequest, Dict]) -> Tuple[Dict, int]:
    """
    登录接口：
    - body: { sid_or_username, password } 或你 OpenAPI 里定义的字段
    - 这里示例用 sid 登录，你可以改为 username 或两者兼容
    """
    stub = _get_db_stub()
    data = _body_to_dict(body)

    sid = data.get("sid")
    password = data.get("password")

    if not sid or not password:
        return _error("sid and password are required", 400)

    password_hash = hashlib.sha256(password.encode("utf-8")).hexdigest()

    try:
        # 如果你是用 username 登录，就改为 GetUserByUsernameRequest
        req = db_pb2.GetUserBySidRequest(sid=sid)
        user = stub.GetUserBySid(req)
    except grpc.RpcError as e:
        if e.code() == grpc.StatusCode.NOT_FOUND:
            return _error("User not found", 404)
        return _error(f"DB service error: {e.code().name} - {e.details()}", 502)

    # 校验密码
    if user.password_hash != password_hash:
        return _error("Invalid password", 401)

    token = _create_jwt_for_user(user)

    resp_data = {
        "user": _grpc_user_to_profile(user),
        "token": token,
    }
    return _success("Login successful", resp_data, 200)


# ====== Controller: get current user profile ======

def users_me_get() -> Tuple[Dict, int]:
    """
    获取当前登录用户信息：
    - 从 JWT 拿 user_id 或 sid
    - 再调 gRPC GetUserBySid / GetUserById
    """
    payload, err = _get_current_user_payload()
    if err is not None:
        return err

    stub = _get_db_stub()
    sid = payload.get("sid")

    try:
        req = db_pb2.GetUserBySidRequest(sid=sid)
        user = stub.GetUserBySid(req)
    except grpc.RpcError as e:
        if e.code() == grpc.StatusCode.NOT_FOUND:
            return _error("User not found", 404)
        return _error(f"DB service error: {e.code().name} - {e.details()}", 502)

    return _success("User profile fetched", _grpc_user_to_profile(user), 200)


# ====== Controller: update current user profile ======

def users_me_patch(body: Union[UserUpdateRequest, Dict]) -> Tuple[Dict, int]:
    """
    更新当前用户信息（不改密码）：
    - body: { username?, email? }
    - 用 JWT 里的 user_id / sid 确认是谁
    """
    payload, err = _get_current_user_payload()
    if err is not None:
        return err

    stub = _get_db_stub()
    sid = payload.get("sid")
    data = _body_to_dict(body)

    # 先拿到当前 user
    try:
        get_req = db_pb2.GetUserBySidRequest(sid=sid)
        user = stub.GetUserBySid(get_req)
    except grpc.RpcError as e:
        if e.code() == grpc.StatusCode.NOT_FOUND:
            return _error("User not found", 404)
        return _error(f"DB service error: {e.code().name} - {e.details()}", 502)

    new_username = data.get("username", user.username)
    new_email = data.get("email", user.email)

    try:
        update_req = db_pb2.UpdateUserRequest(
            id=user.id,
            sid=user.sid,
            username=new_username,
            email=new_email,
            password_hash=user.password_hash,  # 不修改密码
        )
        updated = stub.UpdateUser(update_req)
    except grpc.RpcError as e:
        return _error(f"DB service error: {e.code().name} - {e.details()}", 502)

    return _success("User profile updated", _grpc_user_to_profile(updated), 200)


# ====== Controller: deactivate current user ======

def users_me_delete() -> Tuple[Dict, int]:
    """
    注销 / 停用当前用户：
    - 这里简单起见：直接 DeleteUser
    - 如果你 DB 有 is_active 字段，可以改成 UpdateUser 设 is_active=false
    """
    payload, err = _get_current_user_payload()
    if err is not None:
        return err

    stub = _get_db_stub()
    sid = payload.get("sid")

    try:
        get_req = db_pb2.GetUserBySidRequest(sid=sid)
        user = stub.GetUserBySid(get_req)
    except grpc.RpcError as e:
        if e.code() == grpc.StatusCode.NOT_FOUND:
            return _error("User not found", 404)
        return _error(f"DB service error: {e.code().name} - {e.details()}", 502)

    try:
        del_req = db_pb2.DeleteUserRequest(id=user.id)
        stub.DeleteUser(del_req)
    except grpc.RpcError as e:
        return _error(f"DB service error: {e.code().name} - {e.details()}", 502)

    return _success("User deactivated", None, 200)
