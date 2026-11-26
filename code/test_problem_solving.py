"""Minh chứng cho Phần 3.3: check-out với giờ ra sai (giờ ra < giờ vào) phải KHÔNG đổi state."""
from datetime import datetime, timedelta

import pytest

from parking_app import ParkingLot

IN = datetime(2026, 3, 1, 8, 0)
A = "59A-00001"


class TestPS33InvalidCheckOutTime:
    def setup_method(self):
        self.lot = ParkingLot(2)
        self.lot.check_in(A, "MOTORBIKE", IN)

    def test_negative_clock_skew_raises_invalid_time(self):
        with pytest.raises(ValueError, match="INVALID_TIME"):
            self.lot.check_out(A, IN - timedelta(minutes=5))

    def test_negative_clock_skew_keeps_vehicle_occupied_and_revenue(self):
        with pytest.raises(ValueError):
            self.lot.check_out(A, IN - timedelta(minutes=5))
        assert A in self.lot.inside
        assert self.lot.occupied == 1
        assert self.lot.revenue == 0

    def test_positive_retry_with_correct_time_succeeds(self):
        with pytest.raises(ValueError):
            self.lot.check_out(A, IN - timedelta(minutes=5))
        assert self.lot.check_out(A, IN + timedelta(hours=1)) == 5_000
        assert self.lot.occupied == 0
        assert self.lot.revenue == 5_000
