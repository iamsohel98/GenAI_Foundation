"""
pytest test suite for TravelPlanner.
Run with:  pytest test_travel_planner.py -v
"""

import pytest
from datetime import date
from travel_planner import TravelPlanner


# ------------------------------------------------------------------ #
#  Fixtures                                                            #
# ------------------------------------------------------------------ #

@pytest.fixture
def planner():
    """Return a fresh, empty TravelPlanner instance."""
    return TravelPlanner()


@pytest.fixture
def loaded_planner():
    """Return a TravelPlanner with a valid trip already added."""
    p = TravelPlanner()
    p.add_trip("Paris, France", "2026-08-10", "2026-08-20", 3500.00)
    return p


# ------------------------------------------------------------------ #
#  __init__                                                            #
# ------------------------------------------------------------------ #

class TestInit:
    def test_all_fields_none_on_creation(self, planner):
        assert planner.destination is None
        assert planner.start_date is None
        assert planner.end_date is None
        assert planner.budget is None


# ------------------------------------------------------------------ #
#  add_trip – happy paths                                              #
# ------------------------------------------------------------------ #

class TestAddTripValid:
    def test_sets_destination(self, planner):
        planner.add_trip("Tokyo", "2026-01-01", "2026-01-10", 2000)
        assert planner.destination == "Tokyo"

    def test_sets_start_date_as_date_object(self, planner):
        planner.add_trip("Tokyo", "2026-01-01", "2026-01-10", 2000)
        assert planner.start_date == date(2026, 1, 1)

    def test_sets_end_date_as_date_object(self, planner):
        planner.add_trip("Tokyo", "2026-01-01", "2026-01-10", 2000)
        assert planner.end_date == date(2026, 1, 10)

    def test_sets_budget_as_float(self, planner):
        planner.add_trip("Tokyo", "2026-01-01", "2026-01-10", 2000)
        assert planner.budget == 2000.0
        assert isinstance(planner.budget, float)

    def test_accepts_integer_budget(self, planner):
        planner.add_trip("Rome", "2026-03-01", "2026-03-05", 1500)
        assert planner.budget == 1500.0

    def test_strips_destination_whitespace(self, planner):
        planner.add_trip("  Berlin  ", "2026-05-01", "2026-05-10", 1000)
        assert planner.destination == "Berlin"

    def test_same_start_and_end_date_allowed(self, planner):
        planner.add_trip("London", "2026-06-15", "2026-06-15", 500)
        assert planner.start_date == planner.end_date

    def test_prints_success_message(self, planner, capsys):
        planner.add_trip("Madrid", "2026-07-01", "2026-07-05", 800)
        captured = capsys.readouterr()
        assert "Madrid" in captured.out
        assert "successfully" in captured.out


# ------------------------------------------------------------------ #
#  add_trip – error paths                                              #
# ------------------------------------------------------------------ #

class TestAddTripInvalid:
    def test_raises_if_trip_already_exists(self, loaded_planner):
        with pytest.raises(RuntimeError, match="already exists"):
            loaded_planner.add_trip("Tokyo", "2026-09-01", "2026-09-10", 1000)

    def test_raises_on_empty_destination(self, planner):
        with pytest.raises(ValueError, match="non-empty string"):
            planner.add_trip("", "2026-01-01", "2026-01-10", 1000)

    def test_raises_on_whitespace_destination(self, planner):
        with pytest.raises(ValueError, match="non-empty string"):
            planner.add_trip("   ", "2026-01-01", "2026-01-10", 1000)

    def test_raises_on_non_string_destination(self, planner):
        with pytest.raises(ValueError):
            planner.add_trip(123, "2026-01-01", "2026-01-10", 1000)

    def test_raises_on_invalid_start_date_format(self, planner):
        with pytest.raises(ValueError, match="YYYY-MM-DD"):
            planner.add_trip("Tokyo", "01-01-2026", "2026-01-10", 1000)

    def test_raises_on_invalid_end_date_format(self, planner):
        with pytest.raises(ValueError, match="YYYY-MM-DD"):
            planner.add_trip("Tokyo", "2026-01-01", "10/01/2026", 1000)

    def test_raises_on_empty_start_date(self, planner):
        with pytest.raises(ValueError):
            planner.add_trip("Tokyo", "", "2026-01-10", 1000)

    def test_raises_when_end_before_start(self, planner):
        with pytest.raises(ValueError, match="on or after"):
            planner.add_trip("Tokyo", "2026-01-10", "2026-01-01", 1000)

    def test_raises_on_zero_budget(self, planner):
        with pytest.raises(ValueError, match="greater than zero"):
            planner.add_trip("Tokyo", "2026-01-01", "2026-01-10", 0)

    def test_raises_on_negative_budget(self, planner):
        with pytest.raises(ValueError, match="greater than zero"):
            planner.add_trip("Tokyo", "2026-01-01", "2026-01-10", -500)

    def test_raises_on_string_budget(self, planner):
        with pytest.raises(ValueError):
            planner.add_trip("Tokyo", "2026-01-01", "2026-01-10", "3500")

    def test_raises_on_boolean_budget(self, planner):
        with pytest.raises(ValueError):
            planner.add_trip("Tokyo", "2026-01-01", "2026-01-10", True)

    def test_state_unchanged_after_failed_add(self, planner):
        """Partial validation failure must not corrupt object state."""
        with pytest.raises(ValueError):
            planner.add_trip("Tokyo", "2026-01-01", "2026-01-10", -1)
        assert planner.destination is None
        assert planner.budget is None


# ------------------------------------------------------------------ #
#  calculate_trip_duration                                             #
# ------------------------------------------------------------------ #

class TestCalculateTripDuration:
    def test_multi_day_trip(self, loaded_planner):
        # 2026-08-10 to 2026-08-20 inclusive = 11 days
        assert loaded_planner.calculate_trip_duration() == 11

    def test_single_day_trip(self, planner):
        planner.add_trip("Oslo", "2026-03-05", "2026-03-05", 300)
        assert planner.calculate_trip_duration() == 1

    def test_month_boundary(self, planner):
        planner.add_trip("Vienna", "2026-01-30", "2026-02-02", 400)
        assert planner.calculate_trip_duration() == 4

    def test_raises_without_trip(self, planner):
        with pytest.raises(RuntimeError, match="add_trip"):
            planner.calculate_trip_duration()


# ------------------------------------------------------------------ #
#  update_budget                                                       #
# ------------------------------------------------------------------ #

class TestUpdateBudget:
    def test_updates_budget_value(self, loaded_planner):
        loaded_planner.update_budget(5000)
        assert loaded_planner.budget == 5000.0

    def test_budget_stored_as_float(self, loaded_planner):
        loaded_planner.update_budget(4000)
        assert isinstance(loaded_planner.budget, float)

    def test_prints_old_and_new_budget(self, loaded_planner, capsys):
        loaded_planner.update_budget(4000)
        captured = capsys.readouterr()
        assert "3,500.00" in captured.out
        assert "4,000.00" in captured.out

    def test_raises_without_trip(self, planner):
        with pytest.raises(RuntimeError):
            planner.update_budget(1000)

    def test_raises_on_zero_budget(self, loaded_planner):
        with pytest.raises(ValueError, match="greater than zero"):
            loaded_planner.update_budget(0)

    def test_raises_on_negative_budget(self, loaded_planner):
        with pytest.raises(ValueError, match="greater than zero"):
            loaded_planner.update_budget(-100)

    def test_raises_on_string_budget(self, loaded_planner):
        with pytest.raises(ValueError):
            loaded_planner.update_budget("5000")

    def test_raises_on_boolean_budget(self, loaded_planner):
        with pytest.raises(ValueError):
            loaded_planner.update_budget(True)


# ------------------------------------------------------------------ #
#  display_trip / __str__                                              #
# ------------------------------------------------------------------ #

class TestDisplayTrip:
    def test_str_contains_destination(self, loaded_planner):
        assert "Paris, France" in str(loaded_planner)

    def test_str_contains_start_date(self, loaded_planner):
        assert "2026-08-10" in str(loaded_planner)

    def test_str_contains_end_date(self, loaded_planner):
        assert "2026-08-20" in str(loaded_planner)

    def test_str_contains_duration(self, loaded_planner):
        assert "11 day(s)" in str(loaded_planner)

    def test_str_contains_budget(self, loaded_planner):
        assert "3,500.00" in str(loaded_planner)

    def test_display_trip_prints_output(self, loaded_planner, capsys):
        loaded_planner.display_trip()
        captured = capsys.readouterr()
        assert "Paris, France" in captured.out

    def test_str_raises_without_trip(self, planner):
        with pytest.raises(RuntimeError):
            str(planner)

    def test_display_trip_raises_without_trip(self, planner):
        with pytest.raises(RuntimeError):
            planner.display_trip()


# ------------------------------------------------------------------ #
#  reset_trip                                                          #
# ------------------------------------------------------------------ #

class TestResetTrip:
    def test_clears_all_fields(self, loaded_planner):
        loaded_planner.reset_trip()
        assert loaded_planner.destination is None
        assert loaded_planner.start_date is None
        assert loaded_planner.end_date is None
        assert loaded_planner.budget is None

    def test_allows_new_add_trip_after_reset(self, loaded_planner):
        loaded_planner.reset_trip()
        loaded_planner.add_trip("Tokyo", "2026-12-01", "2026-12-10", 2000)
        assert loaded_planner.destination == "Tokyo"

    def test_prints_cleared_message(self, loaded_planner, capsys):
        loaded_planner.reset_trip()
        captured = capsys.readouterr()
        assert "cleared" in captured.out.lower()

    def test_reset_on_empty_planner_is_safe(self, planner):
        """Resetting an already-empty planner should not raise."""
        planner.reset_trip()
        assert planner.destination is None


# ------------------------------------------------------------------ #
#  estimate_hotel_expenses                                             #
# ------------------------------------------------------------------ #

class TestEstimateHotelExpenses:
    def test_default_ratio_hotel_budget(self, loaded_planner):
        # 40% of 3500 = 1400
        result = loaded_planner.estimate_hotel_expenses()
        assert result["total_hotel_budget"] == 1400.00

    def test_default_ratio_remaining_budget(self, loaded_planner):
        result = loaded_planner.estimate_hotel_expenses()
        assert result["remaining_budget"] == 2100.00

    def test_default_ratio_nights(self, loaded_planner):
        # 11 days => 10 nights
        result = loaded_planner.estimate_hotel_expenses()
        assert result["nights"] == 10

    def test_default_ratio_nightly_rate(self, loaded_planner):
        # 1400 / 10 = 140.00
        result = loaded_planner.estimate_hotel_expenses()
        assert result["nightly_rate"] == 140.00

    def test_custom_ratio_hotel_budget(self, loaded_planner):
        result = loaded_planner.estimate_hotel_expenses(0.50)
        assert result["total_hotel_budget"] == 1750.00

    def test_custom_ratio_remaining_budget(self, loaded_planner):
        result = loaded_planner.estimate_hotel_expenses(0.50)
        assert result["remaining_budget"] == 1750.00

    def test_ratio_of_one_allocates_full_budget(self, loaded_planner):
        result = loaded_planner.estimate_hotel_expenses(1.0)
        assert result["total_hotel_budget"] == 3500.00
        assert result["remaining_budget"] == 0.00

    def test_return_type_is_dict(self, loaded_planner):
        result = loaded_planner.estimate_hotel_expenses()
        assert isinstance(result, dict)

    def test_dict_has_required_keys(self, loaded_planner):
        result = loaded_planner.estimate_hotel_expenses()
        assert set(result.keys()) == {
            "total_hotel_budget", "nightly_rate", "nights", "remaining_budget"
        }

    def test_single_day_trip_nights_minimum_one(self, planner):
        planner.add_trip("Oslo", "2026-03-05", "2026-03-05", 300)
        result = planner.estimate_hotel_expenses()
        assert result["nights"] == 1

    def test_raises_without_trip(self, planner):
        with pytest.raises(RuntimeError):
            planner.estimate_hotel_expenses()

    def test_raises_on_zero_ratio(self, loaded_planner):
        with pytest.raises(ValueError, match="0 .exclusive."):
            loaded_planner.estimate_hotel_expenses(0)

    def test_raises_on_ratio_above_one(self, loaded_planner):
        with pytest.raises(ValueError):
            loaded_planner.estimate_hotel_expenses(1.1)

    def test_raises_on_negative_ratio(self, loaded_planner):
        with pytest.raises(ValueError):
            loaded_planner.estimate_hotel_expenses(-0.5)

    def test_raises_on_boolean_ratio(self, loaded_planner):
        with pytest.raises(ValueError):
            loaded_planner.estimate_hotel_expenses(True)

    def test_raises_on_string_ratio(self, loaded_planner):
        with pytest.raises(ValueError):
            loaded_planner.estimate_hotel_expenses("0.4")


# ------------------------------------------------------------------ #
#  display_hotel_expenses                                              #
# ------------------------------------------------------------------ #

class TestDisplayHotelExpenses:
    def test_prints_hotel_budget(self, loaded_planner, capsys):
        loaded_planner.display_hotel_expenses()
        assert "1,400.00" in capsys.readouterr().out

    def test_prints_nightly_rate(self, loaded_planner, capsys):
        loaded_planner.display_hotel_expenses()
        assert "140.00" in capsys.readouterr().out

    def test_prints_nights(self, loaded_planner, capsys):
        loaded_planner.display_hotel_expenses()
        assert "10" in capsys.readouterr().out

    def test_prints_remaining_budget(self, loaded_planner, capsys):
        loaded_planner.display_hotel_expenses()
        assert "2,100.00" in capsys.readouterr().out

    def test_prints_total_budget(self, loaded_planner, capsys):
        loaded_planner.display_hotel_expenses()
        assert "3,500.00" in capsys.readouterr().out

    def test_custom_ratio_reflected_in_output(self, loaded_planner, capsys):
        loaded_planner.display_hotel_expenses(0.50)
        output = capsys.readouterr().out
        assert "50%" in output
        assert "1,750.00" in output

    def test_raises_without_trip(self, planner):
        with pytest.raises(RuntimeError):
            planner.display_hotel_expenses()
