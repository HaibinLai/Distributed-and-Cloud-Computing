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

from openapi_server.logging_service import logging_client

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
        # 如果裸机，就local host:50051；如果在 Docker 里跑，就 db_service:50051
        target = os.environ.get("DB_GRPC_TARGET", "db_service:50051")
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
        logging_client.send_logs([{
            "service_name": "api-service/user",
            "level": "WARNING",
            "path": connexion.request.path,
            "method": connexion.request.method,
            "user_sid": "",
            "message": "Missing or invalid Authorization header"
        }])
        return None, _error("Missing or invalid Authorization header", 401)

    token = auth_header.split(" ", 1)[1].strip()
    try:
        payload = pyjwt.decode(token, JWT_SECRET, algorithms=[JWT_ALGO])
    except pyjwt.ExpiredSignatureError:
        logging_client.send_logs([{
            "service_name": "api-service/user",
            "level": "WARNING",
            "path": connexion.request.path,
            "method": connexion.request.method,
            "user_sid": "",
            "message": "Token expired"
        }])
        return None, _error("Token expired", 401)
    except pyjwt.InvalidTokenError:
        logging_client.send_logs([{
            "service_name": "api-service/user",
            "level": "WARNING",
            "path": connexion.request.path,
            "method": connexion.request.method,
            "user_sid": "",
            "message": "Invalid token"
        }])
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
        logging_client.send_logs([{
            "service_name": "api-service/user",
            "level": "WARNING",
            "path": connexion.request.path,
            "method": connexion.request.method,
            "user_sid": sid or "",
            "message": "Missing required fields for registration"
        }])
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
            logging_client.send_logs([{
                "service_name": "api-service/user",
                "level": "WARNING",
                "path": connexion.request.path,
                "method": connexion.request.method,
                "user_sid": sid or "",
                "message": f"User already exists: {e.details()}"
            }])
            return _error(f"User already exists: {e.details()}", 409)
        logging_client.send_logs([{
            "service_name": "api-service/user",
            "level": "ERROR",
            "path": connexion.request.path,
            "method": connexion.request.method,
            "user_sid": sid or "",
            "message": f"DB service error: {e.code().name} - {e.details()}"
        }])
        return _error(f"DB service error: {e.code().name} - {e.details()}", 502)

    token = _create_jwt_for_user(user)

    resp_data = {
        "user": _grpc_user_to_profile(user),
        "token": token,
    }
    logging_client.send_logs([{
        "service_name": "api-service/user",
        "level": "INFO",
        "path": connexion.request.path,
        "method": connexion.request.method,
        "user_sid": sid,
        "message": "User registered successfully"
    }])
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
        logging_client.send_logs([{
            "service_name": "api-service/user",
            "level": "WARNING",
            "path": connexion.request.path,
            "method": connexion.request.method,
            "user_sid": sid or "",
            "message": "Missing required fields for login"
        }])
        return _error("sid and password are required", 400)

    password_hash = hashlib.sha256(password.encode("utf-8")).hexdigest()

    try:
        # 如果你是用 username 登录，就改为 GetUserByUsernameRequest
        req = db_pb2.GetUserBySidRequest(sid=sid)
        user = stub.GetUserBySid(req)
    except grpc.RpcError as e:
        if e.code() == grpc.StatusCode.NOT_FOUND:
            logging_client.send_logs([{
                "service_name": "api-service/user",
                "level": "WARNING",
                "path": connexion.request.path,
                "method": connexion.request.method,
                "user_sid": sid or "",
                "message": "User not found"
            }])
            return _error("User not found", 404)
        logging_client.send_logs([{
            "service_name": "api-service/user",
            "level": "ERROR",
            "path": connexion.request.path,
            "method": connexion.request.method,
            "user_sid": sid or "",
            "message": f"DB service error: {e.code().name} - {e.details()}"
        }])
        return _error(f"DB service error: {e.code().name} - {e.details()}", 502)

    # 校验密码
    if user.password_hash != password_hash:
        logging_client.send_logs([{
            "service_name": "api-service/user",
            "level": "WARNING",
            "path": connexion.request.path,
            "method": connexion.request.method,
            "user_sid": sid or "",
            "message": "Invalid password"
        }])
        return _error("Invalid password", 401)

    token = _create_jwt_for_user(user)

    resp_data = {
        "user": _grpc_user_to_profile(user),
        "token": token,
    }
    logging_client.send_logs([{
        "service_name": "api-service/user",
        "level": "INFO",
        "path": connexion.request.path,
        "method": connexion.request.method,
        "user_sid": sid,
        "message": "Login successful"
    }])
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
            logging_client.send_logs([{
                "service_name": "api-service/user",
                "level": "WARNING",
                "path": connexion.request.path,
                "method": connexion.request.method,
                "user_sid": sid or "",
                "message": "User not found"
            }])
            return _error("User not found", 404)
        logging_client.send_logs([{
            "service_name": "api-service/user",
            "level": "ERROR",
            "path": connexion.request.path,
            "method": connexion.request.method,
            "user_sid": sid or "",
            "message": f"DB service error: {e.code().name} - {e.details()}"
        }])
        return _error(f"DB service error: {e.code().name} - {e.details()}", 502)

    logging_client.send_logs([{
        "service_name": "api-service/user",
        "level": "INFO",
        "path": connexion.request.path,
        "method": connexion.request.method,
        "user_sid": sid,
        "message": "User profile fetched successfully"
    }])
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
            logging_client.send_logs([{
                "service_name": "api-service/user",
                "level": "ERROR",
                "path": connexion.request.path,
                "method": connexion.request.method,
                "user_sid": sid or "",
                "message": "User not found"
            }])
            return _error("User not found", 404)
        logging_client.send_logs([{
            "service_name": "api-service/user",
            "level": "ERROR",
            "path": connexion.request.path,
            "method": connexion.request.method,
            "user_sid": sid or "",
            "message": f"DB service error: {e.code().name} - {e.details()}"
        }])
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
        logging_client.send_logs([{
            "service_name": "api-service/user",
            "level": "ERROR",
            "path": connexion.request.path,
            "method": connexion.request.method,
            "user_sid": sid or "",
            "message": f"DB service error: {e.code().name} - {e.details()}"
        }])
        return _error(f"DB service error: {e.code().name} - {e.details()}", 502)

    logging_client.send_logs([{
        "service_name": "api-service/user",
        "level": "INFO",
        "path": connexion.request.path,
        "method": connexion.request.method,
        "user_sid": sid,
        "message": "User profile updated successfully"
    }])
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
            logging_client.send_logs([{
                "service_name": "api-service/user",
                "level": "ERROR",
                "path": connexion.request.path,
                "method": connexion.request.method,
                "user_sid": sid or "",
                "message": "User not found"
            }])
            return _error("User not found", 404)
        logging_client.send_logs([{
            "service_name": "api-service/user",
            "level": "ERROR",
            "path": connexion.request.path,
            "method": connexion.request.method,
            "user_sid": sid or "",
            "message": f"DB service error: {e.code().name} - {e.details()}"
        }])
        return _error(f"DB service error: {e.code().name} - {e.details()}", 502)

    try:
        del_req = db_pb2.DeleteUserRequest(id=user.id)
        stub.DeleteUser(del_req)
    except grpc.RpcError as e:
        logging_client.send_logs([{
            "service_name": "api-service/user",
            "level": "ERROR",
            "path": connexion.request.path,
            "method": connexion.request.method,
            "user_sid": sid or "",
            "message": f"DB service error: {e.code().name} - {e.details()}"
        }])
        return _error(f"DB service error: {e.code().name} - {e.details()}", 502)

    logging_client.send_logs([{
        "service_name": "api-service/user",
        "level": "INFO",
        "path": connexion.request.path,
        "method": connexion.request.method,
        "user_sid": sid,
        "message": "User deactivated successfully"
    }])
    return _success("User deactivated", None, 200)
