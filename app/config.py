"""Konfigurasi aplikasi. Nilai bisa di-override lewat environment variable."""
import os

APP_NAME = "API Pengelolaan Rumah Kos"
APP_VERSION = "1.0.0"
API_PREFIX = "/api/v1"

# API key -> identitas pengguna. Ganti lewat env di produksi.
API_KEYS: dict[str, dict[str, str]] = {
    os.getenv("KOS_PENGELOLA_KEY", "pengelola-key-2026"): {"user": "pengelola", "role": "PENGELOLA"},
    os.getenv("KOS_ADMIN_KEY", "admin-key-2026"): {"user": "admin", "role": "ADMIN"},
}
