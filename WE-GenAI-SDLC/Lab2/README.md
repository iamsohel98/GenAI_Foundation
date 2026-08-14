# Travel Planner — Lab2

A Python project for managing travel trip details, estimating hotel expenses, running automated tests, and interacting with a conversational chatbot.

---

## Project Structure

```
Lab2/
├── travel_planner.py       # Core TravelPlanner class
├── chatbot.py              # Conversational CLI chatbot
├── test_travel_planner.py  # pytest test suite (46 tests)
├── test_cases.json         # Test case specifications
└── README.md               # This file
```

---

## Requirements

- Python 3.7+
- pytest (for running tests)

Install pytest:

```bash
pip install pytest
```

---

## Files

### `travel_planner.py`

The core `TravelPlanner` class. Manages trip details with full input validation.

**Variables:**

| Variable | Type | Description |
|---|---|---|
| `destination` | `str` | Travel destination name |
| `start_date` | `date` | Trip start date |
| `end_date` | `date` | Trip end date |
| `budget` | `float` | Total trip budget (USD) |

**Methods:**

| Method | Description |
|---|---|
| `add_trip(destination, start_date, end_date, budget)` | Add a new trip with validation |
| `display_trip()` | Print formatted trip summary |
| `calculate_trip_duration()` | Return trip length in days (inclusive) |
| `update_budget(new_budget)` | Update the trip budget |
| `estimate_hotel_expenses(ratio)` | Return hotel cost breakdown as a dict |
| `display_hotel_expenses(ratio)` | Print formatted hotel expense estimate |
| `reset_trip()` | Clear all trip data |

**Usage:**

```python
from travel_planner import TravelPlanner

planner = TravelPlanner()
planner.add_trip("Paris, France", "2026-08-10", "2026-08-20", 3500.00)
planner.display_trip()
planner.display_hotel_expenses()          # default 40% hotel ratio
planner.display_hotel_expenses(0.50)      # custom 50% hotel ratio
planner.update_budget(4000.00)
planner.reset_trip()
```

**Run the demo:**

```bash
python travel_planner.py
```

---

### `chatbot.py`

A conversational CLI chatbot built on top of `TravelPlanner`. Remembers user details across the session and provides personalised travel recommendations.

**Remembers:**
- User name
- Destination
- Travel dates
- Budget

**Recommendation tiers (based on daily spend):**

| Tier | Daily Budget |
|---|---|
| Backpacker | < $50/day |
| Mid-range | $50–$149/day |
| Luxury | $150+/day |

**Available commands (type at any prompt):**

| Command | Action |
|---|---|
| `show` | Display current trip details |
| `recommend` | Show personalised travel tips |
| `reset` | Clear trip data and start over |
| `help` | Show all commands |
| `quit` / `exit` | Exit the chatbot |

**Run the chatbot:**

```bash
python chatbot.py
```

---

### `test_travel_planner.py`

A pytest suite with 46 tests covering all public methods, valid inputs, invalid inputs, error messages, and state integrity.

**Test classes:**

| Class | Tests | Covers |
|---|---|---|
| `TestInit` | 1 | Initial field state |
| `TestAddTripValid` | 8 | Valid `add_trip()` inputs |
| `TestAddTripInvalid` | 13 | All validation error paths |
| `TestCalculateTripDuration` | 4 | Duration calculation |
| `TestUpdateBudget` | 8 | Budget update and validation |
| `TestDisplayTrip` | 8 | `__str__` and `display_trip()` output |
| `TestResetTrip` | 4 | Reset behaviour |

**Run all tests:**

```bash
pytest test_travel_planner.py -v
```

**Run a specific test class:**

```bash
pytest test_travel_planner.py::TestAddTripValid -v
```

---

### `test_cases.json`

A structured JSON specification of all 46 test cases. Each entry includes:
- Unique ID (e.g. `TC_ADD_VALID_001`)
- Test function name
- Description
- Input values
- Expected output or exception

Used as a test reference document independent of the pytest implementation.

---

## Input Validation Rules

| Field | Rules |
|---|---|
| `destination` | Non-empty string; whitespace is stripped |
| `start_date` / `end_date` | `YYYY-MM-DD` format; `end_date` ≥ `start_date` |
| `budget` | Positive `int` or `float`; strings and booleans rejected |
| `hotel_budget_ratio` | `float` in range `(0, 1]`; booleans rejected |

---

## Error Types

| Exception | When raised |
|---|---|
| `ValueError` | Invalid input to any method |
| `RuntimeError` | Calling methods before `add_trip()`, or calling `add_trip()` twice without `reset_trip()` |
