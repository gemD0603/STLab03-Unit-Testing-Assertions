"""Unit test cho PHẦN B (REQ-06 đến REQ-12): lớp ParkingLot có state."""
import os
from datetime import datetime, timedelta

import pytest

from parking_app import ParkingLot

IN = datetime(2026, 3, 1, 8, 0)
A, B, C = "59A-00001", "59A-00002", "59A-00003"


class LotCase:
    """Setup/Teardown dùng chung: mỗi test nhận một bãi xe MỚI (sức chứa 2)."""

    def setup_method(self):
        if os.environ.get("STLAB_TRACE"):          # chỉ để minh chứng số lần setup chạy (E05)
            print("[setup_method]")
        self.lot = ParkingLot(2)

    def teardown_method(self):
        self.lot.inside.clear()


class TestReq06CanEnter(LotCase):
    def test_positive_valid_plate_no_debt_can_enter(self):
        assert self.lot.can_enter("59A-12345") is True

    def test_negative_blacklisted_plate_cannot_enter(self):
        self.lot.blacklist.add("59A-12345")
        assert not self.lot.can_enter("59A-12345")

    def test_negative_invalid_plate_cannot_enter(self):
        assert not self.lot.can_enter("59a-12345")

    @pytest.mark.parametrize("debt, expected", [
        (0, True), (99_999, True), (100_000, False), (100_001, False),
    ])
    def test_edge_debt_around_100000(self, debt, expected):
        self.lot.debts["59A-12345"] = debt
        assert self.lot.can_enter("59A-12345") is expected

    def test_negative_check_in_blacklisted_raises_not_allowed(self):
        self.lot.blacklist.add(A)
        with pytest.raises(ValueError, match="NOT_ALLOWED"):
            self.lot.check_in(A, "CAR", IN)

    def test_edge_check_in_with_debt_exactly_100000_raises_not_allowed(self):
        self.lot.debts[A] = 100_000
        with pytest.raises(ValueError, match="NOT_ALLOWED"):
            self.lot.check_in(A, "CAR", IN)


class TestReq07CheckInSuccess(LotCase):
    def test_positive_occupied_increases_by_one(self):
        self.lot.check_in(A, "CAR", IN)
        assert self.lot.occupied == 1

    def test_positive_vehicle_is_recorded(self):
        self.lot.check_in(A, "MOTORBIKE", IN)
        assert self.lot.inside == {A: ("MOTORBIKE", IN)}

    def test_edge_last_free_slot_can_be_used(self):
        self.lot.check_in(A, "CAR", IN)
        self.lot.check_in(B, "CAR", IN)
        assert self.lot.occupied == 2


class TestReq08LotFull(LotCase):
    def test_negative_full_lot_raises_lot_full(self):
        self.lot.check_in(A, "CAR", IN)
        self.lot.check_in(B, "CAR", IN)
        with pytest.raises(ValueError, match="LOT_FULL"):
            self.lot.check_in(C, "CAR", IN)

    def test_negative_full_lot_keeps_state(self):
        self.lot.check_in(A, "CAR", IN)
        self.lot.check_in(B, "CAR", IN)
        with pytest.raises(ValueError):
            self.lot.check_in(C, "CAR", IN)
        assert self.lot.occupied == 2
        assert set(self.lot.inside) == {A, B}

    def test_edge_lot_with_capacity_zero_is_always_full(self):
        lot = ParkingLot(0)
        with pytest.raises(ValueError, match="LOT_FULL"):
            lot.check_in(A, "CAR", IN)


class TestReq09AlreadyInside(LotCase):
    def test_negative_same_plate_twice_raises_already_inside(self):
        self.lot.check_in(A, "CAR", IN)
        with pytest.raises(ValueError, match="ALREADY_INSIDE"):
            self.lot.check_in(A, "CAR", IN)

    def test_negative_rejected_check_in_keeps_occupied(self):
        self.lot.check_in(A, "CAR", IN)
        with pytest.raises(ValueError):
            self.lot.check_in(A, "CAR", IN)
        assert self.lot.occupied == 1
        assert self.lot.inside == {A: ("CAR", IN)}

    def test_edge_plate_can_check_in_again_after_check_out(self):
        self.lot.check_in(A, "CAR", IN)
        self.lot.check_out(A, IN + timedelta(hours=1))
        self.lot.check_in(A, "CAR", IN + timedelta(hours=2))
        assert self.lot.occupied == 1

    def test_edge_full_lot_reports_lot_full_before_already_inside(self):
        lot = ParkingLot(1)
        lot.check_in(A, "CAR", IN)
        with pytest.raises(ValueError, match="LOT_FULL"):
            lot.check_in(A, "CAR", IN)


class TestReq10CheckOut(LotCase):
    def test_positive_returns_fee(self):
        self.lot.check_in(A, "MOTORBIKE", IN)
        assert self.lot.check_out(A, IN + timedelta(hours=3)) == 5_000

    def test_positive_state_after_check_out(self):
        self.lot.check_in(A, "CAR", IN)
        self.lot.check_out(A, IN + timedelta(minutes=90))
        assert self.lot.occupied == 0
        assert A not in self.lot.inside

    def test_positive_revenue_accumulates(self):
        self.lot.check_in(A, "CAR", IN)
        self.lot.check_in(B, "MOTORBIKE", IN)
        self.lot.check_out(A, IN + timedelta(hours=1))        # 20.000
        self.lot.check_out(B, IN + timedelta(hours=1))        # 5.000
        assert self.lot.revenue == 25_000

    def test_edge_exactly_four_hours_motorbike_costs_5000(self):
        self.lot.check_in(A, "MOTORBIKE", IN)
        assert self.lot.check_out(A, IN + timedelta(minutes=240)) == 5_000

    def test_edge_revenue_starts_at_zero(self):
        assert self.lot.revenue == 0


class TestReq11CheckOutNotInside(LotCase):
    def test_negative_never_checked_in_raises_not_inside(self):
        with pytest.raises(ValueError, match="NOT_INSIDE"):
            self.lot.check_out(A, IN)

    def test_negative_second_check_out_raises_not_inside(self):
        self.lot.check_in(A, "CAR", IN)
        self.lot.check_out(A, IN + timedelta(hours=1))
        with pytest.raises(ValueError, match="NOT_INSIDE"):
            self.lot.check_out(A, IN + timedelta(hours=2))

    def test_negative_rejected_check_out_keeps_state(self):
        self.lot.check_in(A, "CAR", IN)
        with pytest.raises(ValueError):
            self.lot.check_out(B, IN + timedelta(hours=1))
        assert self.lot.occupied == 1
        assert self.lot.revenue == 0


class TestReq12LostTicket(LotCase):
    def test_positive_lost_ticket_adds_50000_to_fee(self):
        self.lot.check_in(A, "MOTORBIKE", IN)
        assert self.lot.check_out(A, IN + timedelta(hours=1), lost_ticket=True) == 55_000

    def test_positive_lost_ticket_adds_50000_to_revenue(self):
        self.lot.check_in(A, "MOTORBIKE", IN)
        self.lot.check_out(A, IN + timedelta(hours=1), lost_ticket=True)
        assert self.lot.revenue == 55_000

    def test_edge_no_lost_ticket_has_no_surcharge(self):
        self.lot.check_in(A, "MOTORBIKE", IN)
        fee = self.lot.check_out(A, IN + timedelta(hours=1), lost_ticket=False)
        assert fee == 5_000
        assert self.lot.revenue == 5_000

    def test_edge_surcharge_is_added_after_the_cap(self):
        self.lot.check_in(A, "MOTORBIKE", IN)
        assert self.lot.check_out(A, IN + timedelta(hours=20), lost_ticket=True) == 80_000

    def test_negative_lost_ticket_but_not_inside_raises(self):
        with pytest.raises(ValueError, match="NOT_INSIDE"):
            self.lot.check_out(A, IN, lost_ticket=True)
