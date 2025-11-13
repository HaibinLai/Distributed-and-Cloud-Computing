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

USERS = {}  # key: sid, value: dict with user info + password
NEXT_USER_ID = 1
CURRENT_SID = None  # fake "logged-in" user sid


def _now_iso():
    return datetime.now(timezone.utc).isoformat().replace("+00:00", "Z")


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


def _user_public_view(user_dict):
    """Strip password, only return fields给前端。"""
    if user_dict is None:
        return None
    return {
        "id": user_dict["id"],
        "sid": user_dict["sid"],
        "username": user_dict.get("username"),
        "email": user_dict.get("email"),
        "created_at": user_dict["created_at"],
        "is_active": user_dict["is_active"],
    }


# ===== Controller Implementations =====


def users_login_post(user_login_request=None):  # noqa: E501
    """Login and get JWT (FAKE)."""

    global CURRENT_SID

    if connexion.request.is_json:
        user_login_request = UserLoginRequest.from_dict(
            connexion.request.get_json()
        )

    sid = user_login_request.sid
    password = user_login_request.password

    user = USERS.get(sid)
    if user is None or not user["is_active"]:
        return _error("User not found or deactivated", 401)

    if user["password"] != password:
        return _error("Invalid credentials", 401)

    CURRENT_SID = sid

    fake_token = f"fake-jwt-token-for-{sid}"

    # data 里放 user + token，后面可以直接替换成真实 JWT
    data = {
        "user": _user_public_view(user),
        "token": fake_token
    }
    return _success("Login successful", data, 200)


def users_me_delete():  # noqa: E501
    """Deactivate current user's account (FAKE)."""

    global CURRENT_SID

    if CURRENT_SID is None or CURRENT_SID not in USERS:
        return _error("Not logged in", 401)

    user = USERS[CURRENT_SID]
    user["is_active"] = False
    CURRENT_SID = None

    return _success("User deactivated successfully", None, 200)


def users_me_get():  # noqa: E501
    """Get current user's profile (FAKE)."""

    if CURRENT_SID is None or CURRENT_SID not in USERS:
        return _error("Not logged in", 401)

    user = USERS[CURRENT_SID]
    if not user["is_active"]:
        return _error("User is deactivated", 401)

    return _success("Current user profile", _user_public_view(user), 200)


def users_me_patch(user_update_request=None):  # noqa: E501
    """Update current user's profile (FAKE)."""

    if CURRENT_SID is None or CURRENT_SID not in USERS:
        return _error("Not logged in", 401)

    if connexion.request.is_json:
        user_update_request = UserUpdateRequest.from_dict(
            connexion.request.get_json()
        )

    user = USERS[CURRENT_SID]

    # 可选字段：username / email / password
    if user_update_request.username is not None:
        user["username"] = user_update_request.username
    if user_update_request.email is not None:
        user["email"] = user_update_request.email
    if getattr(user_update_request, "password", None) is not None:
        user["password"] = user_update_request.password

    return _success("User updated successfully", _user_public_view(user), 200)


def users_register_post(user_register_request=None):  # noqa: E501
    """Register a new user (FAKE)."""

    global NEXT_USER_ID, CURRENT_SID

    if connexion.request.is_json:
        user_register_request = UserRegisterRequest.from_dict(
            connexion.request.get_json()
        )

    sid = user_register_request.sid
    password = user_register_request.password
    username = getattr(user_register_request, "username", None)
    email = getattr(user_register_request, "email", None)

    if sid in USERS and USERS[sid]["is_active"]:
        return _error("User already exists", 409)

    created_at = _now_iso()
    user_id = NEXT_USER_ID
    NEXT_USER_ID += 1

    USERS[sid] = {
        "id": user_id,
        "sid": sid,
        "username": username,
        "email": email,
        "password": password,
        "created_at": created_at,
        "is_active": True,
    }

    CURRENT_SID = sid  # 注册后自动“登录”

    fake_token = f"fake-jwt-token-for-{sid}"
    data = {
        "user": _user_public_view(USERS[sid]),
        "token": fake_token
    }
    return _success("User registered successfully", data, 201)
