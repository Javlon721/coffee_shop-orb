from typing import Annotated
from fastapi import Depends, HTTPException, Security, status
from fastapi.security import OAuth2PasswordBearer, SecurityScopes

from auth.models import AccessToken, AccessTokenData
from auth.utils import create_access_token, decode_token, get_roles_from
from roles.models import AvailableRoles
from users.models import UserWithRoles
from users.repository import UsersRepository


oauth2_scheme = OAuth2PasswordBearer(tokenUrl="auth/login", refreshUrl="auth/refresh")


def get_current_user(security_scopes: SecurityScopes, token: Annotated[str, Depends(oauth2_scheme)]) -> UserWithRoles:
  if security_scopes.scopes:
    authenticate_value = f'Bearer scope="{security_scopes.scope_str}"'
  else:
    authenticate_value = "Bearer"

  credentials_exception = \
    HTTPException( 
      status_code=status.HTTP_401_UNAUTHORIZED, 
      detail="Could not validate credentials", 
      headers={"WWW-Authenticate": authenticate_value},
    )

  try:
    payload = decode_token(token)
    user_id = payload.get("sub")

    if user_id is None:
      raise credentials_exception

    token_roles = get_roles_from(payload)

    token_data = AccessTokenData(sub=user_id, roles=token_roles)

  except Exception:
    raise credentials_exception

  assert token_data.sub is not None
  user = UsersRepository.get_user(token_data.sub)

  if user is None:
    raise credentials_exception

  for scope in security_scopes.scopes:
    if scope not in token_data.roles:
      raise HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Not enough permissions",
        headers={"WWW-Authenticate": authenticate_value},
      )
  return UserWithRoles(user=user, roles=token_data.roles)


def renew_access_token(token: Annotated[str, Depends(oauth2_scheme)]) -> AccessToken:
  credentials_exception = \
    HTTPException(
      status_code=status.HTTP_401_UNAUTHORIZED,
      detail="Could not validate credentials",
      headers={"WWW-Authenticate": "Bearer"},
    )

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


def is_admin(user: UserWithRoles) -> bool:
  return AvailableRoles.ADMIN in user.roles


AdminDependency = Security(get_current_user, scopes=[AvailableRoles.ADMIN])
ValidUserDependency = Security(get_current_user, scopes=[])