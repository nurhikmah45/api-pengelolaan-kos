from tests.conftest import ADMIN, BASE, KAMAR, PENGELOLA, buat_kamar, buat_penghuni, buat_sewa


def test_root_service(client):
    res = client.get("/")
    assert res.status_code == 200
    assert res.json()["service"] == "API Pengelolaan Rumah Kos"


def test_create_kamar_normalizes_data(client):
    res = client.post(f"{BASE}/kamar", json={**KAMAR, "fasilitas": [" Kasur ", "kasur", "WiFi"]}, headers=PENGELOLA)
    assert res.status_code == 201
    data = res.json()
    assert data["nomor_kamar"] == "A1"
    assert data["fasilitas"] == ["kasur", "wifi"]
    assert data["status"] == "tersedia"


def test_create_kamar_duplicate_number_conflict(client, kamar):
    res = client.post(f"{BASE}/kamar", json=KAMAR, headers=PENGELOLA)
    assert res.status_code == 409
    assert res.json()["code"] == "CONFLICT"


def test_create_kamar_invalid_price_422(client):
    res = client.post(f"{BASE}/kamar", json={**KAMAR, "harga_bulanan": 5000}, headers=PENGELOLA)
    assert res.status_code == 422
    assert res.json()["details"][0]["field"] == "body -> harga_bulanan"


def test_create_kamar_invalid_number_format_422(client):
    res = client.post(f"{BASE}/kamar", json={**KAMAR, "nomor_kamar": "KAMAR-1"}, headers=PENGELOLA)
    assert res.status_code == 422


def test_list_kamar_filters(client):
    buat_kamar(client, nomor_kamar="A1", harga_bulanan=700000, tipe="standar")
    buat_kamar(client, nomor_kamar="B2", harga_bulanan=1200000, tipe="premium", lantai=2)
    assert client.get(f"{BASE}/kamar", params={"tipe": "premium"}).json()["total"] == 1
    assert client.get(f"{BASE}/kamar", params={"harga_maks": 800000}).json()["total"] == 1
    assert client.get(f"{BASE}/kamar", params={"lantai": 2}).json()["items"][0]["nomor_kamar"] == "B2"
    assert len(client.get(f"{BASE}/kamar", params={"limit": 1}).json()["items"]) == 1


def test_get_kamar_not_found(client):
    res = client.get(f"{BASE}/kamar/99")
    assert res.status_code == 404


def test_patch_kamar_set_maintenance(client, kamar):
    res = client.patch(f"{BASE}/kamar/{kamar['id']}", json={"status": "perbaikan"}, headers=PENGELOLA)
    assert res.status_code == 200
    assert res.json()["status"] == "perbaikan"


def test_patch_kamar_cannot_set_terisi_manually(client, kamar):
    res = client.patch(f"{BASE}/kamar/{kamar['id']}", json={"status": "terisi"}, headers=PENGELOLA)
    assert res.status_code == 422


def test_patch_kamar_occupied_status_locked(client, sewa):
    res = client.patch(f"{BASE}/kamar/{sewa['kamar_id']}", json={"status": "tersedia"}, headers=PENGELOLA)
    assert res.status_code == 400


def test_delete_kamar_requires_admin(client, kamar):
    assert client.delete(f"{BASE}/kamar/{kamar['id']}", headers=PENGELOLA).status_code == 403
    assert client.delete(f"{BASE}/kamar/{kamar['id']}", headers=ADMIN).status_code == 204


def test_delete_kamar_with_history_conflict(client, sewa):
    assert client.delete(f"{BASE}/kamar/{sewa['kamar_id']}", headers=ADMIN).status_code == 409
