"""
travel_planner.py
=================
Core module for the Travel Planner application.

Provides the ``TravelPlanner`` class, which manages a single trip's
destination, dates, and budget. All public methods perform full input
validation before mutating state, so the object is always either clean
or fully populated — never partially initialised.

Typical usage
-------------
    from travel_planner import TravelPlanner

    planner = TravelPlanner()
    planner.add_trip("Paris, France", "2026-08-10", "2026-08-20", 3500.00)
    planner.display_trip()
    planner.display_hotel_expenses()   # default 40 % hotel ratio
    planner.update_budget(4000.00)
    planner.reset_trip()               # clear and start over
"""

from datetime import date
from typing import Optional


class TravelPlanner:
    """Manages travel planning including destination, dates, and budget."""

    DATE_FORMAT = "%Y-%m-%d"
    DISPLAY_WIDTH = 40
    # Default share of total budget allocated to hotel costs (40%).
    DEFAULT_HOTEL_BUDGET_RATIO = 0.40

    # Explicit type annotations make instance variables self-documenting.
    destination: Optional[str]
    start_date: Optional[date]
    end_date: Optional[date]
    budget: Optional[float]

    def __init__(self):
        """
        Initialise TravelPlanner with all fields set to ``None``.

        No trip is active until :meth:`add_trip` is called successfully.
        All four instance variables start as ``None`` so that
        :meth:`_require_trip` can detect an uninitialised state reliably.
        """
        self.destination: Optional[str] = None
        self.start_date: Optional[date] = None
        self.end_date: Optional[date] = None
        self.budget: Optional[float] = None

    # ------------------------------------------------------------------ #
    #  Public Methods                                                      #
    # ------------------------------------------------------------------ #

    def add_trip(self, destination: str, start_date: str, end_date: str, budget: float) -> None:
        """
        Add a new trip with destination, dates, and budget.

        Args:
            destination (str): Name of the travel destination.
            start_date  (str): Trip start date in YYYY-MM-DD format.
            end_date    (str): Trip end date in YYYY-MM-DD format.
            budget      (float): Total budget for the trip (must be > 0).

        Raises:
            RuntimeError: If a trip already exists (call reset_trip() first).
            ValueError: If any input fails validation.
        """
        # Prevent silent overwrite of an existing trip.
        if self.destination is not None:
            raise RuntimeError("A trip already exists. Call reset_trip() before adding a new one.")

        # Validate destination
        if not isinstance(destination, str) or not destination.strip():
            raise ValueError("Destination must be a non-empty string.")

        # Parse and validate dates
        parsed_start = self._parse_date(start_date, "start_date")
        parsed_end = self._parse_date(end_date, "end_date")

        if parsed_end < parsed_start:
            raise ValueError("end_date must be on or after start_date.")

        # Validate budget
        budget = self._validate_budget(budget)

        # Assign validated values only after all checks pass.
        self.destination = destination.strip()
        self.start_date = parsed_start
        self.end_date = parsed_end
        self.budget = budget

        print(f"Trip to '{self.destination}' added successfully.")

    def __str__(self) -> str:
        """
        Return a formatted string of the current trip details.

        Raises:
            RuntimeError: If no trip has been added yet.
        """
        self._require_trip()
        # Use internal helper to avoid a redundant _require_trip() call.
        duration = self._calculate_duration()
        sep = "=" * self.DISPLAY_WIDTH
        return (
            f"\n{sep}\n"
            f"         TRIP DETAILS\n"
            f"{sep}\n"
            f"  Destination : {self.destination}\n"
            f"  Start Date  : {self.start_date.strftime(self.DATE_FORMAT)}\n"
            f"  End Date    : {self.end_date.strftime(self.DATE_FORMAT)}\n"
            f"  Duration    : {duration} day(s)\n"
            f"  Budget      : ${self.budget:,.2f}\n"
            f"{sep}\n"
        )

    def display_trip(self) -> None:
        """
        Print the current trip details to the console.

        Raises:
            RuntimeError: If no trip has been added yet.
        """
        print(self)

    def calculate_trip_duration(self) -> int:
        """
        Calculate the number of days between start and end dates (inclusive).

        Both the start and end dates are counted, so a trip from
        2026-08-10 to 2026-08-20 returns 11, not 10.

        Returns:
            int: Trip duration in days (always >= 1).

        Raises:
            RuntimeError: If no trip has been added yet.
        """
        self._require_trip()
        return self._calculate_duration()

    def estimate_hotel_expenses(self, hotel_budget_ratio: float = DEFAULT_HOTEL_BUDGET_RATIO) -> dict:
        """
        Estimate hotel expenses based on the total trip budget.

        Splits the budget into a hotel portion and a remaining portion, then
        derives a nightly rate from the trip duration.

        Args:
            hotel_budget_ratio (float): Fraction of the total budget to allocate
                to hotel costs. Must be between 0 (exclusive) and 1 (inclusive).
                Defaults to DEFAULT_HOTEL_BUDGET_RATIO (40%).

        Returns:
            dict with keys:
                - total_hotel_budget (float): Budget allocated to hotel.
                - nightly_rate       (float): Estimated cost per night.
                - nights             (int):   Number of nights (duration - 1).
                - remaining_budget   (float): Budget left for other expenses.

        Raises:
            RuntimeError: If no trip has been added yet.
            ValueError: If hotel_budget_ratio is not between 0 and 1.
        """
        self._require_trip()

        if not isinstance(hotel_budget_ratio, (int, float)) or isinstance(hotel_budget_ratio, bool):
            raise ValueError("hotel_budget_ratio must be a numeric value.")
        if not (0 < hotel_budget_ratio <= 1):
            raise ValueError("hotel_budget_ratio must be between 0 (exclusive) and 1 (inclusive).")

        duration = self._calculate_duration()
        # Number of nights is one less than the number of days.
        nights = max(duration - 1, 1)
        total_hotel_budget = round(self.budget * hotel_budget_ratio, 2)
        nightly_rate = round(total_hotel_budget / nights, 2)
        remaining_budget = round(self.budget - total_hotel_budget, 2)

        return {
            "total_hotel_budget": total_hotel_budget,
            "nightly_rate": nightly_rate,
            "nights": nights,
            "remaining_budget": remaining_budget,
        }

    def display_hotel_expenses(self, hotel_budget_ratio: float = DEFAULT_HOTEL_BUDGET_RATIO) -> None:
        """
        Print a formatted hotel expense estimate to the console.

        Args:
            hotel_budget_ratio (float): Fraction of budget for hotel. Defaults to 40%.

        Raises:
            RuntimeError: If no trip has been added yet.
            ValueError: If hotel_budget_ratio is invalid.
        """
        est = self.estimate_hotel_expenses(hotel_budget_ratio)
        sep = "=" * self.DISPLAY_WIDTH
        print(
            f"\n{sep}\n"
            f"       HOTEL EXPENSE ESTIMATE\n"
            f"{sep}\n"
            f"  Hotel ratio     : {hotel_budget_ratio * 100:.0f}% of total budget\n"
            f"  Total budget    : ${self.budget:,.2f}\n"
            f"  Hotel budget    : ${est['total_hotel_budget']:,.2f}\n"
            f"  Nights          : {est['nights']}\n"
            f"  Est. nightly    : ${est['nightly_rate']:,.2f}/night\n"
            f"  Remaining       : ${est['remaining_budget']:,.2f}\n"
            f"{sep}\n"
        )

    def reset_trip(self) -> None:
        """Clear all trip details, allowing a new trip to be added."""
        self.destination = None
        self.start_date = None
        self.end_date = None
        self.budget = None
        print("Trip data cleared.")

    def update_budget(self, new_budget: float) -> None:
        """
        Update the trip budget.

        Args:
            new_budget (float): The new budget amount (must be > 0).

        Raises:
            RuntimeError: If no trip has been added yet.
            ValueError: If new_budget is invalid.
        """
        self._require_trip()
        new_budget = self._validate_budget(new_budget)

        old_budget = self.budget
        self.budget = new_budget
        print(f"Budget updated: ${old_budget:,.2f} → ${self.budget:,.2f}")

    # ------------------------------------------------------------------ #
    #  Private Helpers                                                     #
    # ------------------------------------------------------------------ #

    def _parse_date(self, date_str: str, field_name: str) -> date:
        """Parse an ISO 8601 date string and return a date object."""
        if not isinstance(date_str, str) or not date_str.strip():
            raise ValueError(f"{field_name} must be a non-empty string.")
        try:
            # date.fromisoformat is faster and clearer than strptime for YYYY-MM-DD.
            return date.fromisoformat(date_str.strip())
        except ValueError as e:
            raise ValueError(
                f"{field_name} '{date_str}' is not a valid date. "
                f"Expected format: YYYY-MM-DD."
            ) from e  # chain original error for full traceback

    @staticmethod
    def _validate_budget(budget: float) -> float:
        """Validate and return a numeric budget value greater than zero."""
        # Reject strings explicitly — coercing "3500" silently can hide caller bugs.
        if not isinstance(budget, (int, float)):
            raise ValueError("Budget must be an int or float, not a string or other type.")
        if isinstance(budget, bool):
            # bool is a subclass of int in Python; treat it as invalid here.
            raise ValueError("Budget must be a numeric value, not a boolean.")
        if budget <= 0:
            raise ValueError("Budget must be greater than zero.")
        return float(budget)

    def _calculate_duration(self) -> int:
        """
        Return trip duration in days (inclusive) without a guard check.

        This is the internal counterpart of :meth:`calculate_trip_duration`.
        It skips the ``_require_trip()`` call deliberately so that methods
        which have already validated state (e.g. ``__str__``,
        ``estimate_hotel_expenses``) avoid a redundant second check.

        Returns:
            int: ``(end_date - start_date).days + 1``
        """
        return (self.end_date - self.start_date).days + 1

    def _require_trip(self) -> None:
        """
        Guard method — raise ``RuntimeError`` if any trip field is ``None``.

        Checking all four fields (not just ``destination``) ensures the
        object cannot be in a partially-populated state that would cause
        silent arithmetic errors downstream.

        Raises:
            RuntimeError: If ``destination``, ``start_date``, ``end_date``,
                or ``budget`` is ``None``.
        """
        if any(v is None for v in (self.destination, self.start_date, self.end_date, self.budget)):
            raise RuntimeError("Incomplete trip data. Please call add_trip() first.")


# ------------------------------------------------------------------ #
#  Quick demo                                                          #
# ------------------------------------------------------------------ #

if __name__ == "__main__":
    planner = TravelPlanner()

    # Add a trip
    planner.add_trip(
        destination="Paris, France",
        start_date="2026-08-10",
        end_date="2026-08-20",
        budget=3500.00,
    )

    # Display trip details
    planner.display_trip()

    # Estimate hotel expenses using default ratio (40%)
    planner.display_hotel_expenses()

    # Estimate hotel expenses with a custom ratio (50%)
    planner.display_hotel_expenses(hotel_budget_ratio=0.50)

    # Calculate duration
    days = planner.calculate_trip_duration()
    print(f"Trip duration: {days} day(s)")

    # Update the budget
    planner.update_budget(4000.00)

    # Confirm updated details
    planner.display_trip()

    # Reset and add a new trip
    planner.reset_trip()
    planner.add_trip(
        destination="Tokyo, Japan",
        start_date="2026-12-01",
        end_date="2026-12-15",
        budget=6000.00,
    )
    planner.display_trip()
