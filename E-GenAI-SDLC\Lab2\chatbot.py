"""
TravelPlannerChatbot - A conversational CLI chatbot that remembers user details
and provides personalized travel recommendations using TravelPlanner.
"""

from travel_planner import TravelPlanner


# ------------------------------------------------------------------ #
#  Recommendation engine                                               #
# ------------------------------------------------------------------ #

def _budget_tier(daily_budget: float) -> str:
    """
    Classify a daily budget into a named tier.

    Args:
        daily_budget (float): Average spend per day in USD.

    Returns:
        str: One of ``'backpacker'`` (< $50), ``'mid-range'`` (< $150),
             or ``'luxury'`` ($150+).
    """
    if daily_budget < 50:
        return "backpacker"
    if daily_budget < 150:
        return "mid-range"
    return "luxury"


RECOMMENDATIONS = {
    "backpacker": [
        "Stay in hostels or guesthouses to keep accommodation costs low.",
        "Use public transport or walk instead of taxis.",
        "Eat at local street food stalls — authentic and cheap.",
        "Look for free walking tours and free museum days.",
        "Travel with a reusable water bottle to avoid buying bottled water.",
    ],
    "mid-range": [
        "Book hotels 4–6 weeks in advance for the best rates.",
        "Mix paid attractions with free ones to balance your spend.",
        "Try lunch menus at restaurants — same food, lower price than dinner.",
        "Use ride-share apps instead of traditional taxis.",
        "Consider a city tourist card for bundled transport and attraction access.",
    ],
    "luxury": [
        "Book airport transfers in advance to avoid inflated on-the-day prices.",
        "Look for early-bird or last-minute deals on premium experiences.",
        "Use a travel credit card to earn points on flights and hotels.",
        "Hire a local guide for private tours — often worth the cost.",
        "Upgrade to business class on long-haul legs only for better value.",
    ],
}


def get_recommendations(planner: TravelPlanner) -> list[str]:
    """
    Build a personalised list of travel tips from a loaded TravelPlanner.

    Selects a base set of tier-appropriate tips (backpacker / mid-range /
    luxury) and appends extra data-driven advice based on trip duration
    and total budget.

    Args:
        planner (TravelPlanner): A TravelPlanner instance with a trip loaded.

    Returns:
        list[str]: Ordered list of human-readable travel tip strings.

    Raises:
        RuntimeError: If ``planner`` has no trip loaded.
    """
    duration = planner.calculate_trip_duration()
    daily = planner.budget / duration
    tier = _budget_tier(daily)
    tips = RECOMMENDATIONS[tier].copy()

    # Add data-driven tips
    if duration > 14:
        tips.append("For long trips, consider doing laundry mid-stay instead of packing extra clothes.")
    if duration <= 3:
        tips.append("Short trip? Pre-book everything to maximise your limited time.")
    if planner.budget > 5000:
        tips.append("With your budget, travel insurance is a worthwhile investment.")

    return tips


# ------------------------------------------------------------------ #
#  Chatbot state                                                       #
# ------------------------------------------------------------------ #

class TravelPlannerChatbot:
    """
    Conversational CLI chatbot for travel planning.

    Collects the user's name, destination, travel dates, and budget
    through a guided prompt flow, persists them for the session, and
    offers personalised travel recommendations via the
    :func:`get_recommendations` engine.

    Attributes:
        name (str | None): The user's name, set during :meth:`_ask_name`.
        planner (TravelPlanner): The underlying trip model.

    Typical flow::

        bot = TravelPlannerChatbot()
        bot.run()   # greet → ask name → collect trip → post-setup menu
    """

    SEPARATOR = "-" * 50

    def __init__(self):
        """
        Initialise the chatbot with an empty name and a fresh TravelPlanner.

        No I/O is performed here; call :meth:`run` to start the session.
        """
        self.planner = TravelPlanner()

    # ------------------------------------------------------------------ #
    #  Greeting & farewell                                                 #
    # ------------------------------------------------------------------ #

    def _greet(self) -> None:
        """Print the welcome banner and usage hints to the console."""
        print("\n" + "=" * 50)
        print("   Welcome to the Travel Planner Chatbot!")
        print("=" * 50)
        print("Type 'help' at any prompt to see available commands.")
        print("Type 'quit' or 'exit' to leave.\n")

    def _farewell(self) -> None:
        """Print a personalised goodbye message using the stored user name."""
        name = self.name or "traveller"
        print(f"\nSafe travels, {name}! Goodbye. ✈")

    # ------------------------------------------------------------------ #
    #  Input helpers                                                       #
    # ------------------------------------------------------------------ #

    @staticmethod
    def _ask(prompt: str) -> str:
        """Read a line of input, stripping whitespace."""
        return input(prompt).strip()

    def _ask_name(self) -> None:
        """
        Prompt the user for their name and store it in ``self.name``.

        Loops until a non-empty name is provided. Intercepts any
        recognised command typed in place of a name.
        """
        while True:
            name = self._ask("What's your name? ")
            if self._is_command(name):
                self._handle_command(name)
                continue
            if name:
                self.name = name
                print(f"\nHi {self.name}! Let's plan your trip.\n")
                return
            print("  Please enter your name.")

    def _ask_destination(self) -> str:
        """
        Prompt the user for a travel destination.

        Returns:
            str: A non-empty destination string.
        """
        while True:
            dest = self._ask(f"Where would you like to travel, {self.name}? ")
            if self._is_command(dest):
                self._handle_command(dest)
                continue
            if dest:
                return dest
            print("  Please enter a destination.")

    def _ask_date(self, label: str) -> str:
        """
        Prompt the user for a date string.

        Args:
            label (str): Display label shown before the input prompt
                         (e.g. ``'Start date'`` or ``'End date'``).

        Returns:
            str: The raw date string as typed (format validation is
                 delegated to :class:`TravelPlanner`).
        """
        while True:
            d = self._ask(f"  {label} (YYYY-MM-DD): ")
            if self._is_command(d):
                self._handle_command(d)
                continue
            if d:
                return d
            print("  Please enter a date.")

    def _ask_budget(self) -> float:
        """
        Prompt the user for a numeric budget value.

        Accepts comma-formatted numbers (e.g. ``"3,500"``). Loops until
        a valid positive float is entered.

        Returns:
            float: The validated budget amount in USD.
        """
        while True:
            raw = self._ask("  What is your total budget (USD)? $")
            if self._is_command(raw):
                self._handle_command(raw)
                continue
            try:
                value = float(raw.replace(",", ""))
                if value <= 0:
                    print("  Budget must be greater than zero.")
                    continue
                return value
            except ValueError:
                print("  Please enter a valid number (e.g. 2500 or 2500.00).")

    # ------------------------------------------------------------------ #
    #  Command handling                                                    #
    # ------------------------------------------------------------------ #

    @staticmethod
    def _is_command(text: str) -> bool:
        """
        Return ``True`` if *text* matches a recognised chatbot command.

        Recognised commands: ``help``, ``quit``, ``exit``, ``show``,
        ``reset``, ``recommend``.

        Args:
            text (str): The string to check (case-insensitive).
        """
        return text.lower() in {"help", "quit", "exit", "show", "reset", "recommend"}

    def _handle_command(self, cmd: str) -> None:
        """
        Dispatch a recognised command string to its handler.

        Args:
            cmd (str): One of the recognised command keywords
                       (case-insensitive).
        """
        cmd = cmd.lower()
        if cmd == "help":
            self._show_help()
        elif cmd in {"quit", "exit"}:
            self._farewell()
            raise SystemExit(0)
        elif cmd == "show":
            self._cmd_show()
        elif cmd == "reset":
            self._cmd_reset()
        elif cmd == "recommend":
            self._cmd_recommend()

    def _show_help(self) -> None:
        """Print the list of available commands to the console."""
        print(f"\n{self.SEPARATOR}")
        print("  Available commands (type at any prompt):")
        print("    show      — display current trip details")
        print("    recommend — show personalised travel tips")
        print("    reset     — clear trip and start over")
        print("    help      — show this message")
        print("    quit/exit — exit the chatbot")
        print(f"{self.SEPARATOR}\n")

    def _cmd_show(self) -> None:
        """
        Display the current trip summary and hotel estimate.

        Prints a notice if no trip has been saved yet.
        """
        if self.planner.destination is None:
            print("\n  No trip saved yet. Complete the setup first.\n")
        else:
            self.planner.display_trip()
            self.planner.display_hotel_expenses()

    def _cmd_reset(self) -> None:
        """
        Prompt for confirmation, then reset the planner and restart
        the trip-collection flow if the user confirms.
        """
        confirm = self._ask("  Reset all trip data? (yes/no): ")
        if confirm.lower() in {"yes", "y"}:
            self.planner.reset_trip()
            print("  Trip cleared. Let's start again.\n")
            self._collect_trip_details()
        else:
            print("  Reset cancelled.\n")

    def _cmd_recommend(self) -> None:
        """
        Show personalised recommendations if a trip is loaded,
        otherwise print a prompt to complete setup first.
        """
        if self.planner.destination is None:
            print("\n  No trip saved yet. Complete the setup first.\n")
            return
        self._show_recommendations()

    # ------------------------------------------------------------------ #
    #  Trip collection flow                                                #
    # ------------------------------------------------------------------ #

    def _collect_trip_details(self) -> None:
        """Walk the user through entering trip details."""
        print(f"\n{self.SEPARATOR}")
        print("  Let's set up your trip details.")
        print(f"{self.SEPARATOR}")

        destination = self._ask_destination()

        print("\n  Enter your travel dates:")
        start_date = self._ask_date("Start date")
        end_date   = self._ask_date("End date  ")

        print("\n  Enter your budget:")
        budget = self._ask_budget()

        # Attempt to save — loop on validation errors
        while True:
            try:
                self.planner.add_trip(destination, start_date, end_date, budget)
                break
            except (ValueError, RuntimeError) as e:
                print(f"\n  Error: {e}")
                # Ask which field to re-enter
                field = self._ask(
                    "  Re-enter which field? (destination / start / end / budget): "
                ).lower()
                if field == "destination":
                    destination = self._ask_destination()
                elif field == "start":
                    start_date = self._ask_date("Start date")
                elif field == "end":
                    end_date = self._ask_date("End date  ")
                elif field == "budget":
                    budget = self._ask_budget()
                else:
                    print("  Unknown field — restarting trip entry.")
                    return self._collect_trip_details()

    # ------------------------------------------------------------------ #
    #  Recommendations display                                             #
    # ------------------------------------------------------------------ #

    def _show_recommendations(self) -> None:
        """
        Print the personalised recommendation list for the current trip.

        Displays the user's name, destination, budget tier, daily spend,
        and a numbered list of tips generated by :func:`get_recommendations`.
        """
        duration = self.planner.calculate_trip_duration()
        daily    = self.planner.budget / duration
        tier     = _budget_tier(daily)
        tips     = get_recommendations(self.planner)

        print(f"\n{self.SEPARATOR}")
        print(f"  Personalised tips for {self.name}'s trip to {self.planner.destination}")
        print(f"  Budget tier : {tier.capitalize()}  (${daily:,.2f}/day)")
        print(self.SEPARATOR)
        for i, tip in enumerate(tips, 1):
            print(f"  {i}. {tip}")
        print(f"{self.SEPARATOR}\n")

    # ------------------------------------------------------------------ #
    #  Post-setup menu                                                     #
    # ------------------------------------------------------------------ #

    def _post_setup_menu(self) -> None:
        """Interactive loop once a trip is saved."""
        while True:
            print(f"\n{self.SEPARATOR}")
            print(f"  Hi {self.name}! Your trip to {self.planner.destination} is saved.")
            print("  What would you like to do?")
            print("    1. Show trip summary")
            print("    2. Show hotel expense estimate")
            print("    3. Get personalised recommendations")
            print("    4. Update budget")
            print("    5. Reset and plan a new trip")
            print("    6. Exit")
            print(self.SEPARATOR)

            choice = self._ask("  Enter choice (1-6): ")

            if self._is_command(choice):
                self._handle_command(choice)
            elif choice == "1":
                self.planner.display_trip()
            elif choice == "2":
                self._hotel_expense_menu()
            elif choice == "3":
                self._show_recommendations()
            elif choice == "4":
                self._update_budget_flow()
            elif choice == "5":
                self._cmd_reset()
            elif choice == "6":
                self._farewell()
                break
            else:
                print("  Invalid choice. Please enter a number between 1 and 6.")

    def _hotel_expense_menu(self) -> None:
        """
        Prompt for an optional custom hotel budget ratio, then display
        the hotel expense estimate.

        Accepts a plain decimal (``0.5``) or percentage string (``50%``).
        Falls back to the default 40 % ratio on invalid input.
        """
        raw = self._ask("  Hotel budget ratio (press Enter for default 40%): ").strip()
        if not raw:
            self.planner.display_hotel_expenses()
        else:
            try:
                ratio = float(raw.strip("%")) / (100 if "%" in raw else 1)
                self.planner.display_hotel_expenses(hotel_budget_ratio=ratio)
            except ValueError:
                print("  Invalid ratio. Using default (40%).")
                self.planner.display_hotel_expenses()

    def _update_budget_flow(self) -> None:
        """
        Prompt the user for a new budget amount and update the planner.

        Loops until a valid positive float is entered or the underlying
        :meth:`TravelPlanner.update_budget` call succeeds.
        """
        while True:
            raw = self._ask(f"  New budget for {self.planner.destination} (USD)? $")
            try:
                new_budget = float(raw.replace(",", ""))
                self.planner.update_budget(new_budget)
                break
            except (ValueError, RuntimeError) as e:
                print(f"  Error: {e}")

    # ------------------------------------------------------------------ #
    #  Main entry point                                                    #
    # ------------------------------------------------------------------ #

    def run(self) -> None:
        """
        Start the interactive chatbot session.

        Execution order:
            1. :meth:`_greet`              — print welcome banner.
            2. :meth:`_ask_name`           — collect and store the user's name.
            3. :meth:`_collect_trip_details` — guided trip-entry flow.
            4. :meth:`_post_setup_menu`    — main action menu loop until exit.
        """
        self._greet()
        self._ask_name()
        self._collect_trip_details()
        self._post_setup_menu()


# ------------------------------------------------------------------ #
#  Launch                                                              #
# ------------------------------------------------------------------ #

if __name__ == "__main__":
    bot = TravelPlannerChatbot()
    bot.run()
