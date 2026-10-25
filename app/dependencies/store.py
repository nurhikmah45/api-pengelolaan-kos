"""Penyedia Store (dependency) agar mudah di-override saat testing."""
from app.repositories.store import Store

_store = Store()


def get_store() -> Store:
    return _store
