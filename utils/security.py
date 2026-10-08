"""Password hashing utilities.

Password disimpan sebagai hash bcrypt (one-way), BUKAN enkripsi yang bisa
di-decrypt. Verifikasi dilakukan dengan membandingkan hash, bukan dengan
mengembalikan plaintext. Ini praktik keamanan standar untuk password.
"""

from __future__ import annotations

import base64
import binascii
from datetime import datetime, timedelta, timezone

import bcrypt
import jwt

from configs.config import settings

# bcrypt membatasi input maksimal 72 byte.
_MAX_BYTES = 72


def hash_password(plain_password: str) -> str:
    """Hash password plaintext menjadi string hash bcrypt."""
    pw = plain_password.encode("utf-8")[:_MAX_BYTES]
    return bcrypt.hashpw(pw, bcrypt.gensalt()).decode("utf-8")


def verify_password(plain_password: str, hashed_password: str) -> bool:
    """Cek apakah plaintext cocok dengan hash. Aman terhadap hash invalid."""
    try:
        pw = plain_password.encode("utf-8")[:_MAX_BYTES]
        return bcrypt.checkpw(pw, hashed_password.encode("utf-8"))
    except (ValueError, TypeError):
        return False


# ---------------------------------------------------------------------------
# JWT access token (ditandatangani) + pembungkus base64
# ---------------------------------------------------------------------------
def _resolve_expire_hours(expire_hours: int | None) -> int:
    """Tentukan masa berlaku token (jam), dibatasi oleh MAX_TOKEN_EXPIRE_HOURS."""
    hours = settings.ACCESS_TOKEN_EXPIRE_HOURS if expire_hours is None else expire_hours
    if hours < 1:
        hours = 1
    if hours > settings.MAX_TOKEN_EXPIRE_HOURS:
        hours = settings.MAX_TOKEN_EXPIRE_HOURS
    return hours


def create_access_token(
    subject: str,
    *,
    extra: dict | None = None,
    expire_hours: int | None = None,
) -> tuple[str, datetime, int]:
    """Buat JWT access token lalu bungkus dengan base64url.

    Mengembalikan (token_base64, waktu_kedaluwarsa_utc, detik_sampai_kedaluwarsa).
    `subject` disimpan di klaim `sub` (dipakai sebagai user id). Token dikembalikan
    sudah dalam bentuk base64 (pembungkus di atas JWT) sesuai permintaan.
    """
    hours = _resolve_expire_hours(expire_hours)
    now = datetime.now(timezone.utc)
    expire = now + timedelta(hours=hours)

    payload: dict = {"sub": subject, "iat": now, "exp": expire}
    if extra:
        payload.update(extra)

    raw_jwt = jwt.encode(payload, settings.SECRET_KEY, algorithm=settings.ALGORITHM)
    token_b64 = encode_base64(raw_jwt)
    expires_in = int((expire - now).total_seconds())
    return token_b64, expire, expires_in


def decode_token(token: str) -> dict:
    """Validasi token.

    Menerima token dalam bentuk base64(JWT) maupun JWT mentah (fallback), lalu
    memvalidasi tanda tangan & masa berlaku JWT. Melempar jwt.PyJWTError jika
    invalid / kedaluwarsa.
    """
    raw_jwt = unwrap_base64(token)
    return jwt.decode(raw_jwt, settings.SECRET_KEY, algorithms=[settings.ALGORITHM])


# ---------------------------------------------------------------------------
# Base64 wrap/unwrap
# ---------------------------------------------------------------------------
def encode_base64(value: str) -> str:
    """Bungkus string menjadi base64url tanpa padding."""
    return base64.urlsafe_b64encode(value.encode("utf-8")).rstrip(b"=").decode("ascii")


def unwrap_base64(token: str) -> str:
    """Buka pembungkus base64. Jika bukan base64 valid, kembalikan apa adanya.

    Ini membuat decode kompatibel baik untuk token base64(JWT) maupun JWT mentah.
    """
    # JWT mentah punya 2 titik (header.payload.signature) -> jangan di-unwrap.
    if token.count(".") == 2:
        return token
    try:
        padding = "=" * (-len(token) % 4)
        decoded = base64.urlsafe_b64decode(token + padding).decode("utf-8")
    except (binascii.Error, ValueError, UnicodeDecodeError):
        return token
    # Hanya anggap hasil decode valid bila menyerupai JWT (2 titik).
    return decoded if decoded.count(".") == 2 else token
