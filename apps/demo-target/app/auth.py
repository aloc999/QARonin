import hashlib
import hmac
import base64
import json
import time

SECRET_KEY = "qaronin-demo-secret-change-me"
TOKEN_TTL_SECONDS = 3600


def _b64url(data: bytes) -> str:
    return base64.urlsafe_b64encode(data).decode().rstrip("=")


def _b64url_decode(data: str) -> bytes:
    padding = "=" * (-len(data) % 4)
    return base64.urlsafe_b64decode(data + padding)


def hash_password(password: str) -> str:
    return hashlib.sha256(password.encode()).hexdigest()


def create_token(username: str, role: str) -> str:
    payload = {
        "sub": username,
        "role": role,
        "iat": int(time.time()),
        "exp": int(time.time()) + TOKEN_TTL_SECONDS,
    }
    body = _b64url(json.dumps(payload).encode())
    sig = _b64url(hmac.new(SECRET_KEY.encode(), body.encode(), hashlib.sha256).digest())
    return f"{body}.{sig}"


class TokenError(Exception):
    pass


def verify_token(token: str) -> dict:
    try:
        body, sig = token.split(".")
    except ValueError:
        raise TokenError("malformed token")
    expected = _b64url(hmac.new(SECRET_KEY.encode(), body.encode(), hashlib.sha256).digest())
    if not hmac.compare_digest(sig, expected):
        raise TokenError("invalid signature")
    payload = json.loads(_b64url_decode(body))
    if payload.get("exp", 0) < time.time():
        raise TokenError("token expired")
    return payload


def authenticate_user(db, username: str, password: str):
    from .models import User

    user = db.query(User).filter(User.username == username).first()
    if user is None or user.password_hash != hash_password(password):
        return None
    return user
