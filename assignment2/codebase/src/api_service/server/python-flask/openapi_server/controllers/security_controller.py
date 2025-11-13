from typing import Optional, Dict


def info_from_bearerAuth(token: str) -> Optional[Dict]:
    """
    Validate fake JWT token and set current user context.

    Token format (for step 1 fake auth):
        "fake-jwt-token-for-{sid}"

    :param token: Token from Authorization header ("Bearer <token>")
    :return: dict with user info if valid, or None if invalid (Connexion 会返回 401)
    """
    # 为了避免循环导入，这里在函数内部导入
    from openapi_server.controllers import users_controller as uc

    if not token:
        return None

    prefix = "fake-jwt-token-for-"
    if not token.startswith(prefix):
        # token 不合法，返回 None -> 401
        return None

    sid = token[len(prefix):]

    user = uc.USERS.get(sid)
    if user is None or not user.get("is_active", False):
        return None

    # 把当前请求的“登录用户”设置到全局，方便你之前基于 CURRENT_SID 的逻辑复用
    uc.CURRENT_SID = sid

    # 返回的字典会作为 token_info 传给 operation（如果函数签名里有 token_info 参数）
    return {
        "uid": user["id"],   # 你可以理解为 user_id
        "sid": sid,
        "sub": sid,          # 有些人习惯把 subject 放 sub 里
    }
