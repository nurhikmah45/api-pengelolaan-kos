"""Kontrak data resource Sewa, Pembayaran, Tagihan, dan Ringkasan."""
from datetime import date, datetime
from enum import Enum

from pydantic import BaseModel, Field, field_validator


class StatusSewa(str, Enum):
    aktif = "aktif"
    selesai = "selesai"
    dibatalkan = "dibatalkan"


class StatusSewaAkhir(str, Enum):
    """Status tujuan yang diizinkan pada PATCH sewa."""
    selesai = "selesai"
    dibatalkan = "dibatalkan"


class MetodeBayar(str, Enum):
    tunai = "tunai"
    transfer = "transfer"
    qris = "qris"


class SewaCreate(BaseModel):
    penghuni_id: int = Field(..., ge=1)
    kamar_id: int = Field(..., ge=1)
    tanggal_mulai: date = Field(..., examples=["2026-11-01"])
    durasi_bulan: int = Field(..., ge=1, le=24, examples=[6])

    @field_validator("tanggal_mulai")
    @classmethod
    def tidak_terlalu_lampau(cls, v: date) -> date:
        if v < date(2020, 1, 1):
            raise ValueError("Tanggal mulai tidak masuk akal (sebelum 2020).")
        return v


class SewaUpdate(BaseModel):
    status: StatusSewaAkhir


class SewaResponse(BaseModel):
    id: int
    penghuni_id: int
    kamar_id: int
    nomor_kamar: str
    tanggal_mulai: date
    tanggal_selesai: date
    durasi_bulan: int
    harga_bulanan: int
    status: StatusSewa
    created_at: datetime


class PembayaranCreate(BaseModel):
    periode: str = Field(..., pattern=r"^\d{4}-(0[1-9]|1[0-2])$", examples=["2026-11"])
    jumlah: int = Field(..., gt=0, le=100_000_000, examples=[850000])
    metode: MetodeBayar = MetodeBayar.transfer
    tanggal_bayar: date = Field(default_factory=date.today)

    @field_validator("tanggal_bayar")
    @classmethod
    def tidak_di_masa_depan(cls, v: date) -> date:
        if v > date.today():
            raise ValueError("Tanggal bayar tidak boleh di masa depan.")
        return v


class PembayaranResponse(BaseModel):
    id: int
    sewa_id: int
    periode: str
    jumlah: int
    metode: MetodeBayar
    tanggal_bayar: date
    created_at: datetime


class StatusTagihan(str, Enum):
    lunas = "lunas"
    belum_bayar = "belum_bayar"
    belum_jatuh_tempo = "belum_jatuh_tempo"


class TagihanItem(BaseModel):
    periode: str
    jumlah_tagihan: int
    status: StatusTagihan


class TagihanResponse(BaseModel):
    sewa_id: int
    total_tagihan: int
    total_terbayar: int
    items: list[TagihanItem]


class RingkasanResponse(BaseModel):
    total_kamar: int
    kamar_tersedia: int
    kamar_terisi: int
    kamar_perbaikan: int
    tingkat_okupansi_persen: float
    total_penghuni: int
    sewa_aktif: int
    total_pendapatan: int
    tunggakan_bulan: int
