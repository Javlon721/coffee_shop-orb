from typing import Annotated
from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer

from auth.models import AccessToken, AccessTokenData, RefreshTokenData
from auth.utils import create_access_token, decode_token


oauth2_scheme = OAuth2PasswordBearer(tokenUrl="auth/login", refreshUrl="auth/refresh")

credentials_exception = HTTPException(
    status_code=status.HTTP_401_UNAUTHORIZED,
    detail="Could not validate credentials",
    headers={"WWW-Authenticate": "Bearer"},
)


def authorize_user(token: Annotated[str, Depends(oauth2_scheme)]) -> AccessTokenData:
    try:
        token_data = AccessTokenData(**decode_token(token))

        if token_data.sub is None:
            raise credentials_exception

        return token_data

    except Exception:
        raise credentials_exception


def renew_access_token(token: Annotated[str, Depends(oauth2_scheme)]) -> AccessToken:
    try:
        token_data = RefreshTokenData(**decode_token(token))
        
        if token_data.sub is None:
          raise credentials_exception
      
        if not token_data.is_refresh:
          raise credentials_exception

        new_access_token_data = AccessTokenData(sub=token_data.sub)
        new_access_token = create_access_token(new_access_token_data.model_dump())
        
        return AccessToken(access_token=new_access_token, token_type="bearer")
    except Exception:
        raise credentials_exception


AuthorizeUserDepends = Depends(authorize_user)
RenewAccessToken = Depends(renew_access_token)