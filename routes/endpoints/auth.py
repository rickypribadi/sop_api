from fastapi import APIRouter, HTTPException, status

from schemas.auth_sch import LoginSch, TokenSch
from schemas.response_sch import PostResponseBaseSch, create_response
from utils.security import create_access_token
import crud

router = APIRouter()


@router.post("/login", response_model=PostResponseBaseSch[TokenSch])
async def login(sch: LoginSch):
    """Login dengan username & password. Mengembalikan access token (base64 JWT).

    Token berlaku default 4 jam (dikonfigurasi via env ACCESS_TOKEN_EXPIRE_HOURS,
    dibatasi MAX_TOKEN_EXPIRE_HOURS). Token adalah JWT yang ditandatangani lalu
    dibungkus base64; kirim sebagai header `Authorization: Bearer <token>`.
    """
    user = await crud.master_user.authenticate(
        username=sch.username, password=sch.password
    )
    if user is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Username atau password salah",
        )

    token, expire_at, expires_in = create_access_token(
        subject=user.id, extra={"username": user.username}
    )

    data = TokenSch(
        access_token=token,
        token_type="bearer",
        expires_in=expires_in,
        expires_at=expire_at,
        user_id=user.id,
        nama=user.nama,
        username=user.username,
    )
    return create_response(data=data, message="Login berhasil")
