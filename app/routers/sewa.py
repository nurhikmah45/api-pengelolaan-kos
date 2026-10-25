"""Endpoint /sewa, pembayaran, dan tagihan."""
from fastapi import APIRouter, Depends, Query, status

from app.dependencies.auth import require_admin_role, verify_api_key
from app.dependencies.store import get_store
from app.repositories.store import Store
from app.schemas.common import ErrorResponse, Page
from app.schemas.sewa import (
    PembayaranCreate, PembayaranResponse, SewaCreate, SewaResponse, SewaUpdate, StatusSewa, TagihanResponse,
)
from app.services.sewa_service import SewaService

router = APIRouter(tags=["Sewa"])


def get_service(store: Store = Depends(get_store)) -> SewaService:
    return SewaService(store)


@router.post(
    "/sewa", response_model=SewaResponse, status_code=status.HTTP_201_CREATED,
    responses={409: {"model": ErrorResponse}}, summary="Buat kontrak sewa",
)
async def create_sewa(
    payload: SewaCreate, service: SewaService = Depends(get_service), _user: dict = Depends(verify_api_key)
):
    return service.create(payload)


@router.get("/sewa", response_model=Page[SewaResponse], summary="Daftar kontrak sewa")
async def list_sewa(
    status: StatusSewa | None = None,
    penghuni_id: int | None = Query(default=None, ge=1),
    kamar_id: int | None = Query(default=None, ge=1),
    limit: int = Query(default=20, ge=1, le=100),
    offset: int = Query(default=0, ge=0),
    service: SewaService = Depends(get_service),
    _user: dict = Depends(verify_api_key),
):
    total, items = service.list(status.value if status else None, penghuni_id, kamar_id, limit, offset)
    return Page(total=total, limit=limit, offset=offset, items=items)


@router.get("/sewa/{sewa_id}", response_model=SewaResponse)
async def get_sewa(
    sewa_id: int, service: SewaService = Depends(get_service), _user: dict = Depends(verify_api_key)
):
    return service.get(sewa_id)


@router.patch("/sewa/{sewa_id}", response_model=SewaResponse, summary="Akhiri / batalkan sewa")
async def update_sewa(
    sewa_id: int, payload: SewaUpdate, service: SewaService = Depends(get_service),
    _user: dict = Depends(verify_api_key),
):
    return service.update_status(sewa_id, payload)


@router.post(
    "/sewa/{sewa_id}/pembayaran", response_model=PembayaranResponse, status_code=status.HTTP_201_CREATED,
    summary="Catat pembayaran sewa per periode",
)
async def create_pembayaran(
    sewa_id: int, payload: PembayaranCreate, service: SewaService = Depends(get_service),
    _user: dict = Depends(verify_api_key),
):
    return service.tambah_pembayaran(sewa_id, payload)


@router.get("/sewa/{sewa_id}/pembayaran", response_model=Page[PembayaranResponse])
async def list_pembayaran(
    sewa_id: int,
    limit: int = Query(default=20, ge=1, le=100),
    offset: int = Query(default=0, ge=0),
    service: SewaService = Depends(get_service),
    _user: dict = Depends(verify_api_key),
):
    total, items = service.list_pembayaran(sewa_id, limit, offset)
    return Page(total=total, limit=limit, offset=offset, items=items)


@router.get("/sewa/{sewa_id}/tagihan", response_model=TagihanResponse, summary="Status tagihan tiap periode")
async def get_tagihan(
    sewa_id: int, service: SewaService = Depends(get_service), _user: dict = Depends(verify_api_key)
):
    return service.tagihan(sewa_id)


@router.delete("/pembayaran/{pembayaran_id}", status_code=status.HTTP_204_NO_CONTENT, summary="Hapus pembayaran (ADMIN)")
async def delete_pembayaran(
    pembayaran_id: int, service: SewaService = Depends(get_service), _admin: dict = Depends(require_admin_role)
):
    service.hapus_pembayaran(pembayaran_id)
