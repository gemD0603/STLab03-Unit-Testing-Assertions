"""Phần 4.1 - Code Interview A, B, C, D. File này chạy riêng, KHÔNG nằm trong Test Report.
Các test có chữ 'bad' là bản SAI (để thấy vì sao sai); chữ 'fixed' là bản đã sửa."""
from datetime import datetime

import pytest

from parking_app import ParkingLot, parking_fee

IN = datetime(2026, 3, 1, 8, 0)


# ---------- A: test không bao giờ đỏ ----------
def fake_parking_fee(vehicle, hours):
    return 0                                   # hàm sai: KHÔNG ném lỗi với xe lạ


def test_A_bad_always_green():
    try:
        fake_parking_fee("TRUCK", 1)
    except ValueError:
        assert True                            # chỉ chạy khi có lỗi; không có lỗi -> không assert nào -> PASS


def test_A_fixed_detects_missing_exception():  # trên hàm sai này test PHẢI ĐỎ (FAIL là đúng ý đồ)
    with pytest.raises(ValueError, match="INVALID_VEHICLE"):
        fake_parking_fee("TRUCK", 1)


def test_A_fixed_on_real_function():
    with pytest.raises(ValueError, match="INVALID_VEHICLE"):
        parking_fee("TRUCK", 1)


# ---------- B: hai lệnh trong pytest.raises ----------
def test_B_bad_same_plate():
    lot = ParkingLot(2)
    with pytest.raises(ValueError):
        lot.check_in("59A-1111", "CAR", IN)    # biển số 4 chữ số -> NOT_ALLOWED, ném lỗi ngay ở dòng này
        lot.check_in("59A-1111", "CAR", IN)    # dòng này KHÔNG BAO GIỜ chạy


def test_B_fixed_same_plate():
    lot = ParkingLot(2)
    lot.check_in("59A-11111", "CAR", IN)       # Arrange: biển số hợp lệ, vào lần 1 (nằm NGOÀI raises)
    with pytest.raises(ValueError, match="ALREADY_INSIDE"):
        lot.check_in("59A-11111", "CAR", IN)   # Act: đúng một lệnh trong raises
    assert lot.occupied == 1                   # Assert state


# ---------- C: expected chép lại code ----------
def test_C_bad_fee():
    hours = 6
    expected = 5_000 + max(0, hours - 4) * 2_000     # chép công thức của code -> sai công thức cũng PASS
    assert parking_fee("MOTORBIKE", hours) == expected


def test_C_fixed_fee():
    assert parking_fee("MOTORBIKE", 6) == 9_000       # tính tay: 5.000 + 2 giờ x 2.000


# ---------- D: dùng chung dữ liệu ----------
class TestLotSharedBad:
    lot = ParkingLot(1)                                # biến cấp lớp, dùng chung giữa các test

    def test_positive_check_in(self):
        self.lot.check_in("59A-11111", "CAR", IN)
        assert self.lot.occupied == 1

    def test_positive_lot_starts_empty(self):          # chạy SAU test trên -> occupied = 1 -> FAIL
        assert self.lot.occupied == 0


class TestLotFixed:
    def setup_method(self):
        self.lot = ParkingLot(1)                       # mỗi test một bãi mới

    def test_positive_check_in(self):
        self.lot.check_in("59A-11111", "CAR", IN)
        assert self.lot.occupied == 1

    def test_positive_lot_starts_empty(self):
        assert self.lot.occupied == 0
