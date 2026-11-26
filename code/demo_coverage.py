"""Phần 3.8 / 9.1 - Coverage cao nhưng test không kiểm tra gì (chạy hết dòng nhưng không assert)."""
from datetime import datetime, timedelta

from parking_app import ParkingLot, occupancy_rate, parked_hours, parking_fee

IN = datetime(2026, 3, 1, 8, 0)


def test_runs_everything_but_checks_nothing():
    parking_fee("MOTORBIKE", 1)
    parking_fee("MOTORBIKE", 30)
    parking_fee("CAR", 30)
    for bad in (lambda: parking_fee("TRUCK", 1), lambda: parking_fee("CAR", 0),
                lambda: occupancy_rate(1, 0), lambda: parked_hours(IN, IN - timedelta(hours=1))):
        try:
            bad()
        except ValueError:
            pass
    occupancy_rate(1, 3)
    lot = ParkingLot(1)
    lot.blacklist.add("59A-99999")
    lot.debts["59A-88888"] = 200_000
    for plate, kind in (("59A-99999", "CAR"), ("59A-88888", "CAR"), ("59A-00001", "TRUCK"),
                        ("59A-00001", "CAR"), ("59A-00002", "CAR"), ("59A-00001", "CAR")):
        try:
            lot.check_in(plate, kind, IN)
        except ValueError:
            pass
    for plate in ("59A-00001", "59A-00009"):
        try:
            lot.check_out(plate, IN + timedelta(hours=3), lost_ticket=True)
        except ValueError:
            pass
