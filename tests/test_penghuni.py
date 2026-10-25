from tests.conftest import ADMIN, BASE, PENGELOLA, PENGHUNI, buat_penghuni


def test_create_penghuni_success(client):
    res = client.post(f"{BASE}/penghuni", json=PENGHUNI, headers=PENGELOLA)
    assert res.status_code == 201
    assert res.json()["nama_lengkap"] == "Siti Aisyah"


def test_penghuni_endpoints_require_api_key(client, penghuni):
    assert client.get(f"{BASE}/penghuni").status_code == 401
    assert client.get(f"{BASE}/penghuni/{penghuni['id']}").status_code == 401


def test_create_penghuni_invalid_phone_422(client):
    res = client.post(f"{BASE}/penghuni", json={**PENGHUNI, "nomor_hp": "12345"}, headers=PENGELOLA)
    assert res.status_code == 422
    assert res.json()["code"] == "VALIDATION_ERROR"


def test_phone_is_cleaned_before_saving(client):
    res = client.post(f"{BASE}/penghuni", json={**PENGHUNI, "nomor_hp": "0812-3456 7890"}, headers=PENGELOLA)
    assert res.json()["nomor_hp"] == "081234567890"


def test_duplicate_phone_conflict(client, penghuni):
    res = client.post(f"{BASE}/penghuni", json={**PENGHUNI, "nama_lengkap": "Budi Santoso"}, headers=PENGELOLA)
    assert res.status_code == 409


def test_list_penghuni_search(client):
    buat_penghuni(client)
    buat_penghuni(client, nama_lengkap="Budi Santoso", nomor_hp="082111222333", pekerjaan="karyawan")
    assert client.get(f"{BASE}/penghuni", params={"q": "budi"}, headers=PENGELOLA).json()["total"] == 1
    assert client.get(f"{BASE}/penghuni", params={"pekerjaan": "karyawan"}, headers=PENGELOLA).json()["total"] == 1


def test_patch_penghuni_partial(client, penghuni):
    res = client.patch(f"{BASE}/penghuni/{penghuni['id']}", json={"pekerjaan": "karyawan"}, headers=PENGELOLA)
    assert res.status_code == 200
    assert res.json()["pekerjaan"] == "karyawan"
    assert res.json()["nama_lengkap"] == penghuni["nama_lengkap"]


def test_delete_penghuni_admin_only(client, penghuni):
    assert client.delete(f"{BASE}/penghuni/{penghuni['id']}", headers=PENGELOLA).status_code == 403
    assert client.delete(f"{BASE}/penghuni/{penghuni['id']}", headers=ADMIN).status_code == 204
