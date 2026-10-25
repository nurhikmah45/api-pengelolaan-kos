"""Logika bisnis Kamar."""
from app.core.errors import BusinessRuleError, ConflictError, NotFoundError
from app.repositories.store import Store, utcnow
from app.schemas.kamar import KamarCreate, KamarUpdate


class KamarService:
    def __init__(self, store: Store):
        self.store = store

    def _nomor_dipakai(self, nomor: str, kecuali_id: int | None = None) -> bool:
        return any(k["nomor_kamar"] == nomor and k["id"] != kecuali_id for k in self.store.kamar.values())

    def create(self, payload: KamarCreate) -> dict:
        if self._nomor_dipakai(payload.nomor_kamar):
            raise ConflictError(f"Kamar nomor '{payload.nomor_kamar}' sudah terdaftar.")
        kamar_id = self.store.next_id("kamar")
        data = {**payload.model_dump(), "id": kamar_id, "status": "tersedia", "created_at": utcnow()}
        self.store.kamar[kamar_id] = data
        return data

    def get(self, kamar_id: int) -> dict:
        kamar = self.store.kamar.get(kamar_id)
        if kamar is None:
            raise NotFoundError(f"Kamar dengan id {kamar_id} tidak ditemukan.")
        return kamar

    def list(self, tipe=None, status=None, lantai=None, harga_maks=None, limit=20, offset=0):
        items = sorted(self.store.kamar.values(), key=lambda k: k["id"])
        if tipe:
            items = [k for k in items if k["tipe"] == tipe]
        if status:
            items = [k for k in items if k["status"] == status]
        if lantai is not None:
            items = [k for k in items if k["lantai"] == lantai]
        if harga_maks is not None:
            items = [k for k in items if k["harga_bulanan"] <= harga_maks]
        return len(items), items[offset : offset + limit]

    def update(self, kamar_id: int, payload: KamarUpdate) -> dict:
        kamar = self.get(kamar_id)
        changes = payload.model_dump(exclude_unset=True)
        if "status" in changes:
            if changes["status"] is None:
                del changes["status"]
            elif kamar["status"] == "terisi":
                raise BusinessRuleError("Status kamar terisi hanya berubah dengan mengakhiri kontrak sewa.")
        kamar.update({k: v for k, v in changes.items() if v is not None})
        return kamar

    def delete(self, kamar_id: int) -> None:
        self.get(kamar_id)
        if any(s["kamar_id"] == kamar_id for s in self.store.sewa.values()):
            raise ConflictError("Kamar memiliki riwayat sewa sehingga tidak dapat dihapus.")
        del self.store.kamar[kamar_id]
