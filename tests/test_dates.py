from datetime import date

from app.core.dates import add_months, daftar_periode, tanggal_selesai


def test_add_months_clamps_end_of_month():
    assert add_months(date(2026, 1, 31), 1) == date(2026, 2, 28)
    assert add_months(date(2028, 1, 31), 1) == date(2028, 2, 29)


def test_add_months_crosses_year():
    assert add_months(date(2026, 11, 15), 3) == date(2027, 2, 15)
    assert add_months(date(2026, 3, 10), -4) == date(2025, 11, 10)


def test_daftar_periode_and_tanggal_selesai():
    assert daftar_periode(date(2026, 11, 20), 3) == ["2026-11", "2026-12", "2027-01"]
    assert tanggal_selesai(date(2026, 11, 20), 3) == date(2027, 2, 19)
