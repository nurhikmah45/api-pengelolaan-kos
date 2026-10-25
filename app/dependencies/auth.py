"""Autentikasi X-API-Key dan otorisasi berbasis peran (RBAC)."""
from fastapi import Depends, Header, HTTPException, status

from app import config


async def verify_api_key(x_api_key: str | None = Header(default=None)) -> dict:
    """401 jika header tidak ada / key tidak dikenal."""
    user = config.API_KEYS.get(x_api_key) if x_api_key else None
    if user is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="API Key tidak ada atau tidak valid.",
            headers={"WWW-Authenticate": "ApiKey"},
        )
    return user


async def require_admin_role(user: dict = Depends(verify_api_key)) -> dict:
    """403 jika pengguna terautentikasi tetapi bukan ADMIN."""
    if user.get("role") != "ADMIN":
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Akses ditolak: operasi ini butuh hak akses ADMIN.",
        )
    return user
