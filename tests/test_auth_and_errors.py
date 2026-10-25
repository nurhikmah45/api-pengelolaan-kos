from app.dependencies.auth import verify_api_key
from app.main import app
from tests.conftest import BASE, KAMAR


def test_post_without_api_key_returns_401(client):
    res = client.post(f"{BASE}/kamar", json=KAMAR)
    assert res.status_code == 401
    assert res.headers["www-authenticate"] == "ApiKey"
    assert res.json()["code"] == "UNAUTHORIZED"


def test_wrong_api_key_returns_401(client):
    assert client.post(f"{BASE}/kamar", json=KAMAR, headers={"X-API-Key": "salah"}).status_code == 401


def test_kamar_listing_is_public_but_ringkasan_is_not(client):
    assert client.get(f"{BASE}/kamar").status_code == 200
    assert client.get(f"{BASE}/ringkasan").status_code == 401


def test_dependency_override_bypasses_auth(client):
    async def fake_user():
        return {"user": "tester", "role": "PENGELOLA"}

    app.dependency_overrides[verify_api_key] = fake_user
    assert client.post(f"{BASE}/kamar", json=KAMAR).status_code == 201


def test_error_format_is_uniform_for_unknown_route(client):
    res = client.get(f"{BASE}/tidak-ada")
    assert res.status_code == 404
    assert set(res.json()) == {"status", "code", "path", "details"}


def test_openapi_docs_available(client):
    paths = client.get("/openapi.json").json()["paths"]
    for p in ("/kamar", "/penghuni", "/sewa", "/sewa/{sewa_id}/tagihan", "/ringkasan"):
        assert f"{BASE}{p}" in paths
