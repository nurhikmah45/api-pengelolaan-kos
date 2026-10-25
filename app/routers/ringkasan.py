"""Endpoint /ringkasan."""
from fastapi import APIRouter, Depends

from app.dependencies.auth import verify_api_key
from app.dependencies.store import get_store
from app.repositories.store import Store
from app.schemas.sewa import RingkasanResponse
from app.services.ringkasan_service import RingkasanService

router = APIRouter(tags=["Ringkasan"])


@router.get("/ringkasan", response_model=RingkasanResponse, summary="Ringkasan okupansi, pendapatan, tunggakan")
async def ringkasan(store: Store = Depends(get_store), _user: dict = Depends(verify_api_key)):
    return RingkasanService(store).hitung()
