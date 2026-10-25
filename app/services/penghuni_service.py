"""Logika bisnis Penghuni."""
from app.core.errors import ConflictError, NotFoundError
from app.repositories.store import Store, utcnow
from app.schemas.penghuni import PenghuniCreate, PenghuniUpdate


class PenghuniService:
    def __init__(self, store: Store):
        self.store = store

    def _hp_dipakai(self, hp: str, kecuali_id: int | None = None) -> bool:
        return any(p["nomor_hp"] == hp and p["id"] != kecuali_id for p in self.store.penghuni.values())

    def create(self, payload: PenghuniCreate) -> dict:
        if self._hp_dipakai(payload.nomor_hp):
            raise ConflictError(f"Nomor HP '{payload.nomor_hp}' sudah terdaftar.")
        pid = self.store.next_id("penghuni")
        data = {**payload.model_dump(), "id": pid, "created_at": utcnow()}
        self.store.penghuni[pid] = data
        return data

    def get(self, penghuni_id: int) -> dict:
        p = self.store.penghuni.get(penghuni_id)
        if p is None:
            raise NotFoundError(f"Penghuni dengan id {penghuni_id} tidak ditemukan.")
        return p

    def list(self, q=None, pekerjaan=None, limit=20, offset=0):
        items = sorted(self.store.penghuni.values(), key=lambda p: p["id"])
        if q:
            items = [p for p in items if q.lower() in p["nama_lengkap"].lower()]
        if pekerjaan:
            items = [p for p in items if p["pekerjaan"] == pekerjaan]
        return len(items), items[offset : offset + limit]

    def update(self, penghuni_id: int, payload: PenghuniUpdate) -> dict:
        p = self.get(penghuni_id)
        changes = payload.model_dump(exclude_unset=True)
        hp = changes.get("nomor_hp")
        if hp and self._hp_dipakai(hp, kecuali_id=penghuni_id):
            raise ConflictError(f"Nomor HP '{hp}' sudah terdaftar.")
        p.update({k: v for k, v in changes.items() if v is not None})
        return p

    def delete(self, penghuni_id: int) -> None:
        self.get(penghuni_id)
        if any(s["penghuni_id"] == penghuni_id for s in self.store.sewa.values()):
            raise ConflictError("Penghuni memiliki riwayat sewa sehingga tidak dapat dihapus.")
        del self.store.penghuni[penghuni_id]
