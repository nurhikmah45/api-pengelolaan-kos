# API Pengelolaan Rumah Kos

REST API (FastAPI) untuk mengelola **kamar**, **penghuni**, **kontrak sewa**, **pembayaran bulanan**, dan **tagihan** sebuah rumah kos.

## Struktur modular
```
app/
├── main.py            # entry point + registrasi router
├── config.py          # konfigurasi & API key
├── core/              # errors.py (handler error seragam), dates.py (utilitas periode)
├── dependencies/      # auth (X-API-Key, RBAC) & store
├── schemas/           # kontrak data Pydantic V2 (Create/Update/Response)
├── services/          # logika bisnis
├── repositories/      # penyimpanan in-memory
└── routers/           # endpoint per domain
tests/                 # 50 unit test (pytest + TestClient)
```

## Menjalankan
```bash
python -m venv .venv && source .venv/bin/activate   # Windows: .venv\Scripts\activate
pip install -r requirements.txt
uvicorn app.main:app --reload
```
Dokumentasi interaktif: http://127.0.0.1:8000/docs

## Test
```bash
pytest -q
```

## Autentikasi (header `X-API-Key`)
| Peran | Key default |
|---|---|
| PENGELOLA | `pengelola-key-2026` |
| ADMIN | `admin-key-2026` |

Ubah lewat env `KOS_PENGELOLA_KEY` / `KOS_ADMIN_KEY`.

## Endpoint (prefix `/api/v1`)
| Method | Path | Akses | Keterangan |
|---|---|---|---|
| GET | `/kamar` | Publik | Filter `tipe`, `status`, `lantai`, `harga_maks`, paginasi |
| POST | `/kamar` | API Key | Tambah kamar (409 jika nomor sama) |
| GET / PATCH | `/kamar/{id}` | Publik / API Key | Detail / ubah sebagian |
| DELETE | `/kamar/{id}` | ADMIN | 409 jika punya riwayat sewa |
| GET/POST | `/penghuni` | API Key | Data pribadi, semua endpoint butuh key |
| GET/PATCH | `/penghuni/{id}` | API Key | Detail / ubah |
| DELETE | `/penghuni/{id}` | ADMIN | 409 jika punya riwayat sewa |
| POST/GET | `/sewa` | API Key | Buat kontrak / daftar (filter `status`, `penghuni_id`, `kamar_id`) |
| GET/PATCH | `/sewa/{id}` | API Key | Detail / akhiri atau batalkan kontrak |
| POST/GET | `/sewa/{id}/pembayaran` | API Key | Catat / lihat pembayaran per periode |
| GET | `/sewa/{id}/tagihan` | API Key | Status tiap periode: lunas, belum_bayar, belum_jatuh_tempo |
| DELETE | `/pembayaran/{id}` | ADMIN | Hapus pembayaran |
| GET | `/ringkasan` | API Key | Okupansi, pendapatan, tunggakan |

## Aturan bisnis
- Kamar hanya bisa disewa jika `tersedia` (terisi → 409, perbaikan → 400).
- Satu penghuni hanya boleh punya satu kontrak aktif.
- Membuat kontrak mengubah kamar menjadi `terisi`; mengakhiri/membatalkan mengembalikannya ke `tersedia`.
- Harga kamar di-*snapshot* saat kontrak dibuat; perubahan harga tidak memengaruhi kontrak berjalan.
- Pembayaran harus pada periode dalam masa sewa, tidak boleh dobel, dan jumlahnya sama dengan tarif bulanan.
- Status `terisi` tidak bisa diubah manual selama kontrak aktif.

## Format error seragam
```json
{"status": "error", "code": "VALIDATION_ERROR", "path": "/api/v1/kamar", "details": [{"field": "body -> harga_bulanan", "msg": "..."}]}
```
