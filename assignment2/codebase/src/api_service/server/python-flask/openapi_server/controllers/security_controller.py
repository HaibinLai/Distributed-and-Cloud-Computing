import os
import jwt
from jwt import InvalidTokenError, ExpiredSignatureError

JWT_SECRET = os.getenv("JWT_SECRET", "dev-secret")
JWT_ALGORITHM = "HS256"

def info_from_bearerAuth(token: str):
    """
    Check and retrieve authentication information from custom bearer token.
    Returned value will be passed in 'token_info' parameter of your operation function, if there is one.
    'sub' or 'uid' will be set in 'user' parameter of your operation function, if there is one.

    :param token: Token provided by Authorization header (without 'Bearer ')
    :type token: str
    :return: Decoded token information or None if token is invalid
    :rtype: dict | None
    """
    try:
        # 解 JWT，验证签名和 exp
        payload = jwt.decode(token, JWT_SECRET, algorithms=[JWT_ALGORITHM])
        # 你登录生成里放了 sid 和 user_id，这里直接返回整个 payload
        return payload
    except ExpiredSignatureError:
        # 过期
        print("[JWT] Token expired")
        return None
    except InvalidTokenError as e:
        # 签名错误 / 格式错误 / 算法不对等都进这里
        print(f"[JWT] Invalid token: {e}")
        return None
