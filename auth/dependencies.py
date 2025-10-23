from typing import Annotated
from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer

from auth.models import AccessToken, AccessTokenData
from auth.utils import create_access_token, decode_token, get_roles_from


oauth2_scheme = OAuth2PasswordBearer(tokenUrl="auth/login", refreshUrl="auth/refresh")

credentials_exception = HTTPException(
  status_code=status.HTTP_401_UNAUTHORIZED,
  detail="Could not validate credentials",
  headers={"WWW-Authenticate": "Bearer"},
)


def authorize_user(token: Annotated[str, Depends(oauth2_scheme)]) -> AccessTokenData:
  try:
    payload = decode_token(token)
    user_id = payload.get("sub")

    if user_id is None:
      raise credentials_exception

    
    token_roles = get_roles_from(payload)

    return AccessTokenData(sub=user_id, roles=token_roles)

  except Exception:
    raise credentials_exception


def renew_access_token(token: Annotated[str, Depends(oauth2_scheme)]) -> AccessToken:
  try:
    payload = decode_token(token)

    user_id = payload.get("sub")

    if user_id is None:
      raise credentials_exception

    is_refresh = payload.get("is_refresh", False)

    if not is_refresh:
      raise credentials_exception

    token_roles = get_roles_from(payload)

    new_access_token_data = AccessTokenData(sub=user_id, roles=token_roles)
    new_access_token = create_access_token(new_access_token_data.model_dump())

    return AccessToken(access_token=new_access_token, token_type="bearer")
  except Exception:
      raise credentials_exception
