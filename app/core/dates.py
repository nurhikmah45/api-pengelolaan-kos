"""Utilitas tanggal & periode (format YYYY-MM)."""
from calendar import monthrange
from datetime import date, timedelta


def add_months(d: date, n: int) -> date:
    """Tambah n bulan; hari dipotong ke akhir bulan jika perlu (31 Jan + 1 bln = 28/29 Feb)."""
    index = d.year * 12 + (d.month - 1) + n
    year, month = divmod(index, 12)
    month += 1
    return date(year, month, min(d.day, monthrange(year, month)[1]))


def periode_str(d: date) -> str:
    return f"{d.year}-{d.month:02d}"


def daftar_periode(mulai: date, durasi_bulan: int) -> list[str]:
    awal = mulai.replace(day=1)
    return [periode_str(add_months(awal, i)) for i in range(durasi_bulan)]


def tanggal_selesai(mulai: date, durasi_bulan: int) -> date:
    return add_months(mulai, durasi_bulan) - timedelta(days=1)
