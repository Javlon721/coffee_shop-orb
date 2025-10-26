from typing import Annotated
from fastapi import Depends, HTTPException, Security, status
from fastapi.security import OAuth2PasswordBearer, SecurityScopes
from jwt import ExpiredSignatureError

from auth.models import AccessToken, AccessTokenData
from auth.utils import create_access_token, decode_token, get_roles_from
from db.connection import AsyncSessionDepends
from roles.models import AvailableRoles
from users.models import UserWithRoles
from users.repository import UsersRepository


oauth2_scheme = OAuth2PasswordBearer(tokenUrl="auth/login", refreshUrl="auth/refresh")


async def get_current_user(
  security_scopes: SecurityScopes, 
  token: Annotated[str, Depends(oauth2_scheme)], 
  session: AsyncSessionDepends
) -> UserWithRoles:
  """
  Its a dependency for user authorization. Purpose is to verify incoming users by accsess token
  to have permissions to endpoints

  :returns: An object containing the authenticated user and their roles.
  :rtype: UserWithRoles

  UserWithRoles Attributes:
      - **user** (*User*): The authenticated user object.
      - **roles** (*list[str]*): List of role names assigned to the user.

  User Attributes:
      - **user_id** (*int)
      - **email** (*str)
      - **password** (*str)
      - **first_name** (*str)
      - **last_name** (*str)
      - **created_at** (*datetime)
      - **is_verified** (*bool)
  """  
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
    user_id = payload.get("user_id")

    if user_id is None:
      raise credentials_exception

    token_roles = get_roles_from(payload)

    token_data = AccessTokenData(user_id=user_id, roles=token_roles)

  except ExpiredSignatureError:
    raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Access token expired")
  except Exception:
    raise credentials_exception

  assert token_data.user_id is not None
  user = await UsersRepository.get_user(session, user_id=token_data.user_id)

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

    user_id = payload.get("user_id")

    if user_id is None:
      raise credentials_exception

    is_refresh = payload.get("is_refresh", False)

    if not is_refresh:
      raise credentials_exception

    token_roles = get_roles_from(payload)

    new_access_token_data = AccessTokenData(user_id=user_id, roles=token_roles)
    new_access_token = create_access_token(new_access_token_data.model_dump())

    return AccessToken(access_token=new_access_token, token_type="bearer")
  except ExpiredSignatureError:
    raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Refresh token expired")
  except Exception:
      raise credentials_exception


def is_admin(user: UserWithRoles) -> bool:
  return AvailableRoles.ADMIN in user.roles


AdminDependency = Security(get_current_user, scopes=[AvailableRoles.ADMIN])
ValidUserDependency = Security(get_current_user, scopes=[])