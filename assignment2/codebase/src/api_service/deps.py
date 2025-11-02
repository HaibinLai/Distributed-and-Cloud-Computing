import os, time, jwt
from fastapi import HTTPException, Depends
from fastapi.security import HTTPBearer
from pydantic import BaseModel

JWT_SECRET = os.getenv("JWT_SECRET", "dev-secret")
JWT_ALG = "HS256"
auth_scheme = HTTPBearer(auto_error=True)

print("[deps] JWT_SECRET:", JWT_SECRET)

class AuthedUser(BaseModel):
    id: int
    username: str

def issue_token(user_id: int, username: str, exp_sec: int = 3600):
    payload = {"sub": str(user_id), "username": username, "exp": int(time.time()) + exp_sec}
    return jwt.encode(payload, JWT_SECRET, algorithm=JWT_ALG)

def require_user(creds = Depends(auth_scheme)) -> AuthedUser:
    token = creds.credentials
    try:
        payload = jwt.decode(token, JWT_SECRET, algorithms=[JWT_ALG])
        return AuthedUser(id=int(payload["sub"]), username=payload["username"])
    except Exception:
        raise HTTPException(status_code=401, detail="Invalid token")
