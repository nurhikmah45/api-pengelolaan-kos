"""Logika bisnis Sewa, Pembayaran, dan Tagihan."""
from datetime import date

from app.core.dates import daftar_periode, periode_str, tanggal_selesai
from app.core.errors import BusinessRuleError, ConflictError, NotFoundError
from app.repositories.store import Store, utcnow
from app.schemas.sewa import PembayaranCreate, SewaCreate, SewaUpdate


class SewaService:
    def __init__(self, store: Store):
        self.store = store

    # ---------- Sewa ----------
    def to_response(self, sewa: dict) -> dict:
        kamar = self.store.kamar.get(sewa["kamar_id"])
        return {**sewa, "nomor_kamar": kamar["nomor_kamar"] if kamar else "-"}

    def create(self, payload: SewaCreate) -> dict:
        penghuni = self.store.penghuni.get(payload.penghuni_id)
        if penghuni is None:
            raise NotFoundError(f"Penghuni dengan id {payload.penghuni_id} tidak ditemukan.")
        kamar = self.store.kamar.get(payload.kamar_id)
        if kamar is None:
            raise NotFoundError(f"Kamar dengan id {payload.kamar_id} tidak ditemukan.")
        if kamar["status"] == "perbaikan":
            raise BusinessRuleError("Kamar sedang dalam perbaikan dan belum bisa disewa.")
        if kamar["status"] == "terisi":
            raise ConflictError("Kamar sedang terisi oleh penghuni lain.")
        if any(s["penghuni_id"] == payload.penghuni_id and s["status"] == "aktif" for s in self.store.sewa.values()):
            raise ConflictError("Penghuni masih memiliki kontrak sewa aktif.")

        sid = self.store.next_id("sewa")
        data = {
            "id": sid,
            "penghuni_id": payload.penghuni_id,
            "kamar_id": payload.kamar_id,
            "tanggal_mulai": payload.tanggal_mulai,
            "tanggal_selesai": tanggal_selesai(payload.tanggal_mulai, payload.durasi_bulan),
            "durasi_bulan": payload.durasi_bulan,
            "harga_bulanan": kamar["harga_bulanan"],  # snapshot harga saat kontrak dibuat
            "status": "aktif",
            "created_at": utcnow(),
        }
        self.store.sewa[sid] = data
        kamar["status"] = "terisi"
        return self.to_response(data)

    def _get_raw(self, sewa_id: int) -> dict:
        sewa = self.store.sewa.get(sewa_id)
        if sewa is None:
            raise NotFoundError(f"Sewa dengan id {sewa_id} tidak ditemukan.")
        return sewa

    def get(self, sewa_id: int) -> dict:
        return self.to_response(self._get_raw(sewa_id))

    def list(self, status=None, penghuni_id=None, kamar_id=None, limit=20, offset=0):
        items = sorted(self.store.sewa.values(), key=lambda s: s["id"])
        if status:
            items = [s for s in items if s["status"] == status]
        if penghuni_id is not None:
            items = [s for s in items if s["penghuni_id"] == penghuni_id]
        if kamar_id is not None:
            items = [s for s in items if s["kamar_id"] == kamar_id]
        return len(items), [self.to_response(s) for s in items[offset : offset + limit]]

    def update_status(self, sewa_id: int, payload: SewaUpdate) -> dict:
        sewa = self._get_raw(sewa_id)
        if sewa["status"] != "aktif":
            raise BusinessRuleError(f"Sewa sudah berstatus '{sewa['status']}' dan tidak dapat diubah lagi.")
        sewa["status"] = payload.status.value
        kamar = self.store.kamar.get(sewa["kamar_id"])
        if kamar is not None:
            kamar["status"] = "tersedia"
        return self.to_response(sewa)

    # ---------- Pembayaran ----------
    def tambah_pembayaran(self, sewa_id: int, payload: PembayaranCreate) -> dict:
        sewa = self._get_raw(sewa_id)
        if sewa["status"] != "aktif":
            raise BusinessRuleError("Pembayaran hanya bisa dicatat untuk sewa yang aktif.")
        if payload.periode not in daftar_periode(sewa["tanggal_mulai"], sewa["durasi_bulan"]):
            raise BusinessRuleError(f"Periode {payload.periode} berada di luar masa sewa.")
        if any(p["sewa_id"] == sewa_id and p["periode"] == payload.periode for p in self.store.pembayaran.values()):
            raise ConflictError(f"Periode {payload.periode} sudah dibayar.")
        if payload.jumlah != sewa["harga_bulanan"]:
            raise BusinessRuleError(f"Jumlah harus sama dengan tarif bulanan Rp{sewa['harga_bulanan']:,}.")
        pid = self.store.next_id("pembayaran")
        data = {**payload.model_dump(), "id": pid, "sewa_id": sewa_id, "created_at": utcnow()}
        self.store.pembayaran[pid] = data
        return data

    def list_pembayaran(self, sewa_id: int, limit=20, offset=0):
        self._get_raw(sewa_id)
        items = sorted(
            (p for p in self.store.pembayaran.values() if p["sewa_id"] == sewa_id), key=lambda p: p["periode"]
        )
        return len(items), items[offset : offset + limit]

    def hapus_pembayaran(self, pembayaran_id: int) -> None:
        if pembayaran_id not in self.store.pembayaran:
            raise NotFoundError(f"Pembayaran dengan id {pembayaran_id} tidak ditemukan.")
        del self.store.pembayaran[pembayaran_id]

    # ---------- Tagihan ----------
    def tagihan(self, sewa_id: int, hari_ini: date | None = None) -> dict:
        sewa = self._get_raw(sewa_id)
        sekarang = periode_str(hari_ini or date.today())
        terbayar = {p["periode"] for p in self.store.pembayaran.values() if p["sewa_id"] == sewa_id}
        items = []
        for periode in daftar_periode(sewa["tanggal_mulai"], sewa["durasi_bulan"]):
            if periode in terbayar:
                status = "lunas"
            elif periode <= sekarang:
                status = "belum_bayar"
            else:
                status = "belum_jatuh_tempo"
            items.append({"periode": periode, "jumlah_tagihan": sewa["harga_bulanan"], "status": status})
        return {
            "sewa_id": sewa_id,
            "total_tagihan": sewa["harga_bulanan"] * sewa["durasi_bulan"],
            "total_terbayar": sewa["harga_bulanan"] * len(terbayar),
            "items": items,
        }
