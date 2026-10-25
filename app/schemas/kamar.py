"""Kontrak data resource Kamar."""
from datetime import datetime
from enum import Enum

from pydantic import BaseModel, Field, field_validator, model_validator


class TipeKamar(str, Enum):
    standar = "standar"
    ber_ac = "ber_ac"
    premium = "premium"


class StatusKamar(str, Enum):
    tersedia = "tersedia"
    terisi = "terisi"
    perbaikan = "perbaikan"


class StatusKamarManual(str, Enum):
    """Status yang boleh diubah manual; 'terisi' hanya lewat kontrak sewa."""
    tersedia = "tersedia"
    perbaikan = "perbaikan"


def _normalisasi_fasilitas(values: list[str] | None) -> list[str] | None:
    if values is None:
        return None
    hasil: list[str] = []
    for v in values:
        v = v.strip().lower()
        if not v:
            raise ValueError("Nama fasilitas tidak boleh kosong.")
        if v not in hasil:
            hasil.append(v)
    return hasil


class KamarCreate(BaseModel):
    nomor_kamar: str = Field(..., pattern=r"^[A-Za-z]?\d{1,3}$", examples=["A12"])
    tipe: TipeKamar = TipeKamar.standar
    lantai: int = Field(..., ge=1, le=10)
    harga_bulanan: int = Field(..., ge=100_000, le=20_000_000, examples=[850000], description="Rupiah per bulan")
    fasilitas: list[str] = Field(default_factory=list, max_length=15, examples=[["kasur", "lemari"]])

    @field_validator("nomor_kamar")
    @classmethod
    def huruf_besar(cls, v: str) -> str:
        return v.upper()

    _fasilitas = field_validator("fasilitas")(_normalisasi_fasilitas)


class KamarUpdate(BaseModel):
    tipe: TipeKamar | None = None
    lantai: int | None = Field(default=None, ge=1, le=10)
    harga_bulanan: int | None = Field(default=None, ge=100_000, le=20_000_000)
    fasilitas: list[str] | None = Field(default=None, max_length=15)
    status: StatusKamarManual | None = None

    _fasilitas = field_validator("fasilitas")(_normalisasi_fasilitas)

    @model_validator(mode="after")
    def minimal_satu_field(self):
        if not self.model_fields_set:
            raise ValueError("Kirim minimal satu field yang ingin diubah.")
        return self


class KamarResponse(BaseModel):
    id: int
    nomor_kamar: str
    tipe: TipeKamar
    lantai: int
    harga_bulanan: int
    fasilitas: list[str]
    status: StatusKamar
    created_at: datetime
