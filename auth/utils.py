

from datetime import timedelta, datetime, timezone
from typing import Any
import jwt
from pwdlib import PasswordHash

from auth.config import AuthConfig


password_hash = PasswordHash.recommended()


def hash_password(password: str) -> str:
  return password_hash.hash(password)


def verify_password(plain_password: str, hashed_password: str) -> bool:
  return password_hash.verify(plain_password, hashed_password)


def create_access_token(data: dict, expires_delta: timedelta | None = None) -> str:
    default_time_delta = timedelta(minutes=AuthConfig.ACCESS_TOKEN_EXPIRE_MINUTES)
    to_encode: dict = data.copy()
    
    if not expires_delta:
        expire = get_expiration_time(default_time_delta)
    else:
        expire = get_expiration_time(expires_delta)

    to_encode["exp"] =  expire

    result = jwt.encode(to_encode, AuthConfig.JWT_SECRET_KEY, algorithm=AuthConfig.JWT_ALGORITHM)

    return result


def create_refresh_token(data: dict[str, Any], expires_delta: timedelta | None = None) -> str:
    default_time_delta = timedelta(hours=AuthConfig.REFRESH_TOKEN_EXPIRE_HOURS)

    to_encode: dict = data.copy()
    
    if not expires_delta:
        expire = get_expiration_time(default_time_delta)
    else:
        expire = get_expiration_time(expires_delta)

    to_encode["exp"] = expire
    to_encode["is_refresh"] = True

    result = jwt.encode(to_encode, AuthConfig.JWT_SECRET_KEY, algorithm=AuthConfig.JWT_ALGORITHM)

    return result


def decode_token(token: str) -> dict[str, Any]:
  return jwt.decode(token, AuthConfig.JWT_SECRET_KEY, algorithms=[AuthConfig.JWT_ALGORITHM])


def get_expiration_time(expires_delta: timedelta) -> datetime:
  return datetime.now(timezone.utc) + expires_delta


def get_roles_from(encoded_data: dict[str, str]) -> list[str]:
  roles = encoded_data.get("roles", "")
  
  return roles.split(" ")