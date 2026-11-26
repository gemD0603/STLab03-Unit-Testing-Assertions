"""Unit test cho PHẦN A (REQ-01 đến REQ-05): các hàm thuần của EduParking.

Expected được suy ra từ requirement (tính tay), KHÔNG chép lại công thức trong code.
"""
from datetime import datetime, timedelta

import pytest

from parking_app import is_valid_plate, occupancy_rate, parked_hours, parking_fee, ParkingLot

IN = datetime(2026, 3, 1, 8, 0)


class TestReq01Plate:
    def test_positive_standard_plate_is_valid(self):
        plate = "59A-12345"                       # Arrange
        result = is_valid_plate(plate)            # Act
        assert result is True                     # Assert (boolean)

    @pytest.mark.parametrize("plate", [
        "", "5A-12345", "59a-12345", "59A12345", "59A-1234", "59A-123456", "5AA-12345", "595-12345",
    ])
    def test_negative_wrong_format_is_invalid(self, plate):
        assert not is_valid_plate(plate)

    @pytest.mark.parametrize("plate", ["00A-00000", "99Z-99999"])
    def test_edge_smallest_and_largest_plate_are_valid(self, plate):
        assert is_valid_plate(plate)


class TestReq02ParkedHours:
    @pytest.mark.parametrize("minutes, expected", [(90, 2), (150, 3), (270, 5)])
    def test_positive_round_up_to_next_hour(self, minutes, expected):
        time_out = IN + timedelta(minutes=minutes)
        assert parked_hours(IN, time_out) == expected

    def test_negative_time_out_before_time_in_raises(self):
        with pytest.raises(ValueError, match="INVALID_TIME"):
            parked_hours(IN, IN - timedelta(minutes=1))

    @pytest.mark.parametrize("minutes, expected", [
        (0, 1), (1, 1), (59, 1), (60, 1), (61, 2), (120, 2), (121, 3),
    ])
    def test_edge_minutes_around_full_hours(self, minutes, expected):
        assert parked_hours(IN, IN + timedelta(minutes=minutes)) == expected

    def test_edge_one_second_over_one_hour_is_two_hours(self):
        assert parked_hours(IN, IN + timedelta(seconds=3601)) == 2


class TestReq03MotorbikeFee:
    @pytest.mark.parametrize("hours, expected", [(6, 9_000), (10, 17_000)])
    def test_positive_fee_after_first_package(self, hours, expected):
        assert parking_fee("MOTORBIKE", hours) == expected

    @pytest.mark.parametrize("hours", [0, -1])
    def test_negative_hours_below_one_raises(self, hours):
        with pytest.raises(ValueError, match="INVALID_HOURS"):
            parking_fee("MOTORBIKE", hours)

    @pytest.mark.parametrize("hours, expected", [
        (1, 5_000), (4, 5_000), (5, 7_000), (16, 29_000), (17, 30_000), (18, 30_000),
    ])
    def test_edge_package_and_cap_boundaries(self, hours, expected):
        assert parking_fee("MOTORBIKE", hours) == expected


class TestReq04CarFee:
    @pytest.mark.parametrize("hours, expected", [(1, 20_000), (3, 30_000), (10, 100_000)])
    def test_positive_car_fee_1_3_10_hours(self, hours, expected):
        assert parking_fee("CAR", hours) == expected

    def test_negative_unknown_vehicle_raises(self):
        with pytest.raises(ValueError, match="INVALID_VEHICLE"):
            parking_fee("TRUCK", 1)

    def test_negative_check_in_unknown_vehicle_raises(self):
        lot = ParkingLot(2)
        with pytest.raises(ValueError, match="INVALID_VEHICLE"):
            lot.check_in("59A-12345", "TRUCK", IN)

    @pytest.mark.parametrize("hours, expected", [
        (2, 20_000), (3, 30_000), (20, 200_000), (21, 200_000), (22, 200_000),
    ])
    def test_edge_package_and_cap_boundaries(self, hours, expected):
        assert parking_fee("CAR", hours) == expected


class TestReq05OccupancyRate:
    def test_positive_one_of_three_is_33_percent(self):
        assert occupancy_rate(1, 3) == pytest.approx(33.3333, abs=1e-4)

    @pytest.mark.parametrize("capacity", [0, -5])
    def test_negative_capacity_not_positive_raises(self, capacity):
        with pytest.raises(ValueError, match="INVALID_CAPACITY"):
            occupancy_rate(1, capacity)

    @pytest.mark.parametrize("occupied, capacity, expected", [(0, 10, 0), (10, 10, 100), (1, 1, 100)])
    def test_edge_empty_and_full_lot(self, occupied, capacity, expected):
        assert occupancy_rate(occupied, capacity) == expected
