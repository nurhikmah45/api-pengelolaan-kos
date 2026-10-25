"""Endpoint /kamar."""
from fastapi import APIRouter, Depends, Query, status

from app.dependencies.auth import require_admin_role, verify_api_key
from app.dependencies.store import get_store
from app.repositories.store import Store
from app.schemas.common import ErrorResponse, Page
from app.schemas.kamar import KamarCreate, KamarResponse, KamarUpdate, StatusKamar, TipeKamar
from app.services.kamar_service import KamarService

router = APIRouter(prefix="/kamar", tags=["Kamar"])


def get_service(store: Store = Depends(get_store)) -> KamarService:
    return KamarService(store)


@router.get("", response_model=Page[KamarResponse], summary="Daftar kamar")
async def list_kamar(
    tipe: TipeKamar | None = None,
    status: StatusKamar | None = None,
    lantai: int | None = Query(default=None, ge=1, le=10),
    harga_maks: int | None = Query(default=None, ge=0),
    limit: int = Query(default=20, ge=1, le=100),
    offset: int = Query(default=0, ge=0),
    service: KamarService = Depends(get_service),
):
    total, items = service.list(
        tipe.value if tipe else None, status.value if status else None, lantai, harga_maks, limit, offset
    )
    return Page(total=total, limit=limit, offset=offset, items=items)


@router.post(
    "", response_model=KamarResponse, status_code=status.HTTP_201_CREATED,
    responses={409: {"model": ErrorResponse}}, summary="Tambah kamar",
)
async def create_kamar(
    payload: KamarCreate, service: KamarService = Depends(get_service), _user: dict = Depends(verify_api_key)
):
    return service.create(payload)


@router.get("/{kamar_id}", response_model=KamarResponse, responses={404: {"model": ErrorResponse}})
async def get_kamar(kamar_id: int, service: KamarService = Depends(get_service)):
    return service.get(kamar_id)


@router.patch("/{kamar_id}", response_model=KamarResponse, summary="Ubah sebagian data kamar")
async def update_kamar(
    kamar_id: int, payload: KamarUpdate, service: KamarService = Depends(get_service),
    _user: dict = Depends(verify_api_key),
):
    return service.update(kamar_id, payload)


@router.delete("/{kamar_id}", status_code=status.HTTP_204_NO_CONTENT, summary="Hapus kamar (ADMIN)")
async def delete_kamar(
    kamar_id: int, service: KamarService = Depends(get_service), _admin: dict = Depends(require_admin_role)
):
    service.delete(kamar_id)
