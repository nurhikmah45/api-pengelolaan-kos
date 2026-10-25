"""Kontrak data resource Penghuni."""
import re
from datetime import datetime
from enum import Enum

from pydantic import BaseModel, Field, field_validator, model_validator

_HP = re.compile(r"^(\+62|62|0)8\d{8,11}$")


class Pekerjaan(str, Enum):
    mahasiswa = "mahasiswa"
    karyawan = "karyawan"
    wiraswasta = "wiraswasta"
    lainnya = "lainnya"


def validasi_hp(value: str | None) -> str | None:
    if value is None:
        return None
    value = value.strip().replace(" ", "").replace("-", "")
    if not _HP.match(value):
        raise ValueError("Nomor HP tidak valid (contoh: 081234567890 atau +6281234567890).")
    return value


def _nama(value: str | None) -> str | None:
    if value is None:
        return None
    value = " ".join(value.split())
    if len(value) < 3:
        raise ValueError("Nama minimal 3 karakter.")
    return value


class PenghuniCreate(BaseModel):
    nama_lengkap: str = Field(..., max_length=80, examples=["Siti Aisyah"])
    nomor_hp: str = Field(..., examples=["081234567890"])
    pekerjaan: Pekerjaan = Pekerjaan.mahasiswa
    kontak_darurat_hp: str | None = Field(default=None, examples=["082345678901"])

    _nama_v = field_validator("nama_lengkap")(_nama)
    _hp_v = field_validator("nomor_hp", "kontak_darurat_hp")(validasi_hp)


class PenghuniUpdate(BaseModel):
    nama_lengkap: str | None = Field(default=None, max_length=80)
    nomor_hp: str | None = None
    pekerjaan: Pekerjaan | None = None
    kontak_darurat_hp: str | None = None

    _nama_v = field_validator("nama_lengkap")(_nama)
    _hp_v = field_validator("nomor_hp", "kontak_darurat_hp")(validasi_hp)

    @model_validator(mode="after")
    def minimal_satu_field(self):
        if not self.model_fields_set:
            raise ValueError("Kirim minimal satu field yang ingin diubah.")
        return self


class PenghuniResponse(BaseModel):
    id: int
    nama_lengkap: str
    nomor_hp: str
    pekerjaan: Pekerjaan
    kontak_darurat_hp: str | None
    created_at: datetime
