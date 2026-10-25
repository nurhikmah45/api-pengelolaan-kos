from datetime import date

from tests.conftest import ADMIN, BASE, PENGELOLA, bulan_ini, buat_kamar, buat_penghuni, buat_sewa


def bayar(client, sewa_id, periode, jumlah=850000):
    return client.post(
        f"{BASE}/sewa/{sewa_id}/pembayaran",
        json={"periode": periode, "jumlah": jumlah, "metode": "qris"},
        headers=PENGELOLA,
    )


def test_create_sewa_occupies_room_and_snapshots_price(client, kamar, penghuni):
    res = buat_sewa(client, kamar["id"], penghuni["id"], mulai=date(2026, 11, 1), durasi=3)
    assert res.status_code == 201
    data = res.json()
    assert data["harga_bulanan"] == 850000
    assert data["tanggal_selesai"] == "2027-01-31"
    assert data["nomor_kamar"] == "A1"
    assert client.get(f"{BASE}/kamar/{kamar['id']}").json()["status"] == "terisi"


def test_price_change_does_not_affect_existing_contract(client, sewa):
    client.patch(f"{BASE}/kamar/{sewa['kamar_id']}", json={"harga_bulanan": 1500000}, headers=PENGELOLA)
    assert client.get(f"{BASE}/sewa/{sewa['id']}", headers=PENGELOLA).json()["harga_bulanan"] == 850000


def test_sewa_occupied_room_conflict(client, sewa):
    penghuni2 = buat_penghuni(client, nama_lengkap="Budi Santoso", nomor_hp="082111222333")
    assert buat_sewa(client, sewa["kamar_id"], penghuni2["id"]).status_code == 409


def test_sewa_room_in_maintenance_rejected(client, kamar, penghuni):
    client.patch(f"{BASE}/kamar/{kamar['id']}", json={"status": "perbaikan"}, headers=PENGELOLA)
    res = buat_sewa(client, kamar["id"], penghuni["id"])
    assert res.status_code == 400


def test_tenant_with_active_contract_cannot_rent_second_room(client, sewa):
    kamar2 = buat_kamar(client, nomor_kamar="B2")
    assert buat_sewa(client, kamar2["id"], sewa["penghuni_id"]).status_code == 409


def test_sewa_unknown_references_404(client, kamar, penghuni):
    assert buat_sewa(client, 999, penghuni["id"]).status_code == 404
    assert buat_sewa(client, kamar["id"], 999).status_code == 404


def test_sewa_invalid_duration_422(client, kamar, penghuni):
    assert buat_sewa(client, kamar["id"], penghuni["id"], durasi=0).status_code == 422
    assert buat_sewa(client, kamar["id"], penghuni["id"], durasi=25).status_code == 422


def test_sewa_requires_api_key(client, kamar, penghuni):
    res = client.post(f"{BASE}/sewa", json={"penghuni_id": 1, "kamar_id": 1, "tanggal_mulai": "2026-11-01", "durasi_bulan": 1})
    assert res.status_code == 401


def test_end_contract_frees_room(client, sewa):
    res = client.patch(f"{BASE}/sewa/{sewa['id']}", json={"status": "selesai"}, headers=PENGELOLA)
    assert res.status_code == 200
    assert res.json()["status"] == "selesai"
    assert client.get(f"{BASE}/kamar/{sewa['kamar_id']}").json()["status"] == "tersedia"


def test_cannot_change_finished_contract(client, sewa):
    client.patch(f"{BASE}/sewa/{sewa['id']}", json={"status": "dibatalkan"}, headers=PENGELOLA)
    res = client.patch(f"{BASE}/sewa/{sewa['id']}", json={"status": "selesai"}, headers=PENGELOLA)
    assert res.status_code == 400


def test_patch_sewa_invalid_status_422(client, sewa):
    res = client.patch(f"{BASE}/sewa/{sewa['id']}", json={"status": "aktif"}, headers=PENGELOLA)
    assert res.status_code == 422


def test_list_sewa_filter_status(client, sewa):
    assert client.get(f"{BASE}/sewa", params={"status": "aktif"}, headers=PENGELOLA).json()["total"] == 1
    assert client.get(f"{BASE}/sewa", params={"status": "selesai"}, headers=PENGELOLA).json()["total"] == 0


def test_pay_rent_success(client, sewa):
    periode = bulan_ini(-2).strftime("%Y-%m")
    res = bayar(client, sewa["id"], periode)
    assert res.status_code == 201
    assert res.json()["periode"] == periode


def test_pay_same_period_twice_conflict(client, sewa):
    periode = bulan_ini(-2).strftime("%Y-%m")
    bayar(client, sewa["id"], periode)
    assert bayar(client, sewa["id"], periode).status_code == 409


def test_pay_wrong_amount_rejected(client, sewa):
    periode = bulan_ini(-2).strftime("%Y-%m")
    assert bayar(client, sewa["id"], periode, jumlah=500000).status_code == 400


def test_pay_period_outside_contract_rejected(client, sewa):
    assert bayar(client, sewa["id"], bulan_ini(-10).strftime("%Y-%m")).status_code == 400


def test_pay_invalid_period_format_422(client, sewa):
    assert bayar(client, sewa["id"], "2026-13").status_code == 422


def test_pay_for_finished_contract_rejected(client, sewa):
    client.patch(f"{BASE}/sewa/{sewa['id']}", json={"status": "selesai"}, headers=PENGELOLA)
    assert bayar(client, sewa["id"], bulan_ini(-2).strftime("%Y-%m")).status_code == 400


def test_tagihan_statuses(client, sewa):
    bayar(client, sewa["id"], bulan_ini(-2).strftime("%Y-%m"))
    data = client.get(f"{BASE}/sewa/{sewa['id']}/tagihan", headers=PENGELOLA).json()
    status = [i["status"] for i in data["items"]]
    assert status == ["lunas", "belum_bayar", "belum_bayar", "belum_jatuh_tempo", "belum_jatuh_tempo", "belum_jatuh_tempo"]
    assert data["total_tagihan"] == 850000 * 6
    assert data["total_terbayar"] == 850000


def test_list_pembayaran_and_admin_delete(client, sewa):
    pay = bayar(client, sewa["id"], bulan_ini(-2).strftime("%Y-%m")).json()
    assert client.get(f"{BASE}/sewa/{sewa['id']}/pembayaran", headers=PENGELOLA).json()["total"] == 1
    assert client.delete(f"{BASE}/pembayaran/{pay['id']}", headers=PENGELOLA).status_code == 403
    assert client.delete(f"{BASE}/pembayaran/{pay['id']}", headers=ADMIN).status_code == 204
    assert client.get(f"{BASE}/sewa/{sewa['id']}/pembayaran", headers=PENGELOLA).json()["total"] == 0


def test_ringkasan(client, sewa):
    bayar(client, sewa["id"], bulan_ini(-2).strftime("%Y-%m"))
    buat_kamar(client, nomor_kamar="B2")
    buat_kamar(client, nomor_kamar="C3")
    client.patch(f"{BASE}/kamar/3", json={"status": "perbaikan"}, headers=PENGELOLA)
    data = client.get(f"{BASE}/ringkasan", headers=PENGELOLA).json()
    assert data == {
        "total_kamar": 3, "kamar_tersedia": 1, "kamar_terisi": 1, "kamar_perbaikan": 1,
        "tingkat_okupansi_persen": 33.3, "total_penghuni": 1, "sewa_aktif": 1,
        "total_pendapatan": 850000, "tunggakan_bulan": 2,
    }
