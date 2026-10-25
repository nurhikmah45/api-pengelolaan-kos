from datetime import date

import pytest
from fastapi.testclient import TestClient

from app.core.dates import add_months
from app.dependencies.store import get_store
from app.main import app
from app.repositories.store import Store

PENGELOLA = {"X-API-Key": "pengelola-key-2026"}
ADMIN = {"X-API-Key": "admin-key-2026"}
BASE = "/api/v1"

KAMAR = {"nomor_kamar": "a1", "tipe": "ber_ac", "lantai": 1, "harga_bulanan": 850000, "fasilitas": ["Kasur", "Lemari"]}
PENGHUNI = {"nama_lengkap": "Siti Aisyah", "nomor_hp": "081234567890", "pekerjaan": "mahasiswa"}


def bulan_ini(offset: int = 0) -> date:
    """Tanggal 1 pada bulan (hari ini + offset bulan)."""
    return add_months(date.today().replace(day=1), offset)


def buat_kamar(client, **override):
    res = client.post(f"{BASE}/kamar", json={**KAMAR, **override}, headers=PENGELOLA)
    assert res.status_code == 201, res.text
    return res.json()


def buat_penghuni(client, **override):
    res = client.post(f"{BASE}/penghuni", json={**PENGHUNI, **override}, headers=PENGELOLA)
    assert res.status_code == 201, res.text
    return res.json()


def buat_sewa(client, kamar_id, penghuni_id, mulai=None, durasi=6):
    res = client.post(
        f"{BASE}/sewa",
        json={"penghuni_id": penghuni_id, "kamar_id": kamar_id,
              "tanggal_mulai": (mulai or bulan_ini(-2)).isoformat(), "durasi_bulan": durasi},
        headers=PENGELOLA,
    )
    return res


@pytest.fixture
def client():
    """Client dengan Store baru untuk setiap test (terisolasi)."""
    store = Store()
    app.dependency_overrides[get_store] = lambda: store
    yield TestClient(app)
    app.dependency_overrides.clear()


@pytest.fixture
def kamar(client):
    return buat_kamar(client)


@pytest.fixture
def penghuni(client):
    return buat_penghuni(client)


@pytest.fixture
def sewa(client, kamar, penghuni):
    res = buat_sewa(client, kamar["id"], penghuni["id"])
    assert res.status_code == 201, res.text
    return res.json()
