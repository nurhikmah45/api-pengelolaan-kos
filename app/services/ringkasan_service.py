"""Ringkasan operasional rumah kos."""
from datetime import date

from app.core.dates import daftar_periode, periode_str
from app.repositories.store import Store


class RingkasanService:
    def __init__(self, store: Store):
        self.store = store

    def hitung(self, hari_ini: date | None = None) -> dict:
        sekarang = periode_str(hari_ini or date.today())
        kamar = list(self.store.kamar.values())
        total = len(kamar)
        terisi = sum(1 for k in kamar if k["status"] == "terisi")
        tunggakan = 0
        for s in self.store.sewa.values():
            if s["status"] != "aktif":
                continue
            terbayar = {p["periode"] for p in self.store.pembayaran.values() if p["sewa_id"] == s["id"]}
            tunggakan += sum(
                1 for per in daftar_periode(s["tanggal_mulai"], s["durasi_bulan"])
                if per <= sekarang and per not in terbayar
            )
        return {
            "total_kamar": total,
            "kamar_tersedia": sum(1 for k in kamar if k["status"] == "tersedia"),
            "kamar_terisi": terisi,
            "kamar_perbaikan": sum(1 for k in kamar if k["status"] == "perbaikan"),
            "tingkat_okupansi_persen": round(terisi / total * 100, 1) if total else 0.0,
            "total_penghuni": len(self.store.penghuni),
            "sewa_aktif": sum(1 for s in self.store.sewa.values() if s["status"] == "aktif"),
            "total_pendapatan": sum(p["jumlah"] for p in self.store.pembayaran.values()),
            "tunggakan_bulan": tunggakan,
        }
