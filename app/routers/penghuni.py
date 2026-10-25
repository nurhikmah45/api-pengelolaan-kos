"""Endpoint /penghuni (data pribadi: seluruh endpoint wajib API Key)."""
from fastapi import APIRouter, Depends, Query, status

from app.dependencies.auth import require_admin_role, verify_api_key
from app.dependencies.store import get_store
from app.repositories.store import Store
from app.schemas.common import ErrorResponse, Page
from app.schemas.penghuni import Pekerjaan, PenghuniCreate, PenghuniResponse, PenghuniUpdate
from app.services.penghuni_service import PenghuniService

router = APIRouter(prefix="/penghuni", tags=["Penghuni"], dependencies=[Depends(verify_api_key)])


def get_service(store: Store = Depends(get_store)) -> PenghuniService:
    return PenghuniService(store)


@router.get("", response_model=Page[PenghuniResponse], summary="Daftar penghuni")
async def list_penghuni(
    q: str | None = Query(default=None, description="Cari nama"),
    pekerjaan: Pekerjaan | None = None,
    limit: int = Query(default=20, ge=1, le=100),
    offset: int = Query(default=0, ge=0),
    service: PenghuniService = Depends(get_service),
):
    total, items = service.list(q, pekerjaan.value if pekerjaan else None, limit, offset)
    return Page(total=total, limit=limit, offset=offset, items=items)


@router.post(
    "", response_model=PenghuniResponse, status_code=status.HTTP_201_CREATED,
    responses={409: {"model": ErrorResponse}}, summary="Daftarkan penghuni",
)
async def create_penghuni(payload: PenghuniCreate, service: PenghuniService = Depends(get_service)):
    return service.create(payload)


@router.get("/{penghuni_id}", response_model=PenghuniResponse, responses={404: {"model": ErrorResponse}})
async def get_penghuni(penghuni_id: int, service: PenghuniService = Depends(get_service)):
    return service.get(penghuni_id)


@router.patch("/{penghuni_id}", response_model=PenghuniResponse)
async def update_penghuni(
    penghuni_id: int, payload: PenghuniUpdate, service: PenghuniService = Depends(get_service)
):
    return service.update(penghuni_id, payload)


@router.delete("/{penghuni_id}", status_code=status.HTTP_204_NO_CONTENT, summary="Hapus penghuni (ADMIN)")
async def delete_penghuni(
    penghuni_id: int, service: PenghuniService = Depends(get_service), _admin: dict = Depends(require_admin_role)
):
    service.delete(penghuni_id)
