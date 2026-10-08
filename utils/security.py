"""Password hashing utilities.

Password disimpan sebagai hash bcrypt (one-way), BUKAN enkripsi yang bisa
di-decrypt. Verifikasi dilakukan dengan membandingkan hash, bukan dengan
mengembalikan plaintext. Ini praktik keamanan standar untuk password.
"""

from __future__ import annotations

import bcrypt

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
