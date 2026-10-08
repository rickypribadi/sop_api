"""Dependency autentikasi JWT (dibungkus base64).

`get_current_user` memvalidasi Bearer token pada header Authorization. Token
dikirim dalam bentuk base64(JWT); `decode_token` membuka pembungkus base64 lalu
memvalidasi tanda tangan & masa berlaku JWT. User dimuat dari klaim `sub`.
"""

from __future__ import annotations

import jwt
from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer

from models.master_user_model import MasterUser
from utils.security import decode_token
import crud

_bearer = HTTPBearer(auto_error=True)

_CREDENTIALS_EXC = HTTPException(
    status_code=status.HTTP_401_UNAUTHORIZED,
    detail="Token tidak valid atau sudah kedaluwarsa",
    headers={"WWW-Authenticate": "Bearer"},
)


async def get_current_user(
    credentials: HTTPAuthorizationCredentials = Depends(_bearer),
) -> MasterUser:
    try:
        payload = decode_token(credentials.credentials)
    except jwt.ExpiredSignatureError:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Token sudah kedaluwarsa",
            headers={"WWW-Authenticate": "Bearer"},
        )
    except jwt.PyJWTError:
        raise _CREDENTIALS_EXC

    user_id = payload.get("sub")
    if not user_id:
        raise _CREDENTIALS_EXC

    user = await crud.master_user.get(id=user_id)
    if user is None or not user.is_active:
        raise _CREDENTIALS_EXC

    return user
