from datetime import datetime

from pydantic import BaseModel


class LoginSch(BaseModel):
    username: str
    password: str


class TokenSch(BaseModel):
    access_token: str        # JWT yang dibungkus base64
    token_type: str = "bearer"
    expires_in: int          # detik sampai kedaluwarsa
    expires_at: datetime     # waktu kedaluwarsa (UTC)
    user_id: str
    nama: str
    username: str
