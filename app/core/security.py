import hashlib
import os
from datetime import UTC, datetime, timedelta

from jose import JWTError, jwt

ALGORITHM = 'HS256'
SECRET_KEY = os.getenv('SECRET_KEY', 'shipyard-dev-secret-key')
ACCESS_TOKEN_EXPIRE_MINUTES = 60


def hash_password(password: str) -> str:
    return hashlib.sha256(password.encode('utf-8')).hexdigest()


def verify_password(password: str, hashed_password: str) -> bool:
    return hash_password(password) == hashed_password


def create_access_token(subject: str, expires_delta: timedelta | None = None) -> str:
    expire = datetime.now(UTC) + (expires_delta or timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES))
    payload = {'sub': subject, 'exp': expire}
    return jwt.encode(payload, SECRET_KEY, algorithm=ALGORITHM)


def decode_access_token(token: str) -> dict[str, str]:
    return jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])


def utc_now() -> datetime:
    return datetime.now(UTC)


def is_token_error(error: Exception) -> bool:
    return isinstance(error, JWTError)
