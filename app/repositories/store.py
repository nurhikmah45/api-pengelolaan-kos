"""Penyimpanan in-memory (repository sederhana)."""
from datetime import datetime, timezone
from itertools import count


def utcnow() -> datetime:
    return datetime.now(timezone.utc)


class Store:
    def __init__(self) -> None:
        self.kamar: dict[int, dict] = {}
        self.penghuni: dict[int, dict] = {}
        self.sewa: dict[int, dict] = {}
        self.pembayaran: dict[int, dict] = {}
        self._seq = {name: count(1) for name in ("kamar", "penghuni", "sewa", "pembayaran")}

    def next_id(self, name: str) -> int:
        return next(self._seq[name])
