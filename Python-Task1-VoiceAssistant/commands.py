"""
Command processing for the Voice Assistant.
"""

import datetime
import webbrowser

from system_info import get_system_info


class CommandProcessor:
    """Process commands received from the user."""

    def __init__(self, speech_manager, user_name):
        self.speech = speech_manager
        self.user_name = user_name

    def tell_time(self):
        """Tell the current time."""

        current_time = datetime.datetime.now().strftime(
            "%I:%M %p"
        )

        self.speech.speak(
            f"The current time is {current_time}."
        )

    def tell_date(self):
        """Tell the current date."""

        current_date = datetime.datetime.now().strftime(
            "%B %d, %Y"
        )

        self.speech.speak(
            f"Today's date is {current_date}."
        )

    def search_web(self, query):
        """Search the web."""

        if not query:
            self.speech.speak(
                "Please tell me what you want to search for."
            )
            return

        self.speech.speak(
            f"Searching for {query}."
        )

        url = (
            "https://www.google.com/search?q="
            + query.replace(" ", "+")
        )

        webbrowser.open(url)

    def show_system_info(self):
        """Read basic system information."""

        information = get_system_info()

        self.speech.speak(
            f"You are using {information['Operating System']}."
        )

        self.speech.speak(
            f"Your Python version is "
            f"{information['Python Version']}."
        )

    def process(self, command):
        """
        Process a command.

        Returns:
            False when the assistant should stop.
            True when it should continue.
        """

        if not command:
            return True

        if any(
            word in command
            for word in ["goodbye", "exit", "quit", "stop"]
        ):
            self.speech.speak(
                f"Goodbye, {self.user_name}. Have a great day!"
            )
            return False

        if any(
            word in command
            for word in ["hello", "hi", "hey"]
        ):
            self.speech.speak(
                f"Hello {self.user_name}. How can I help you?"
            )
            return True

        if "time" in command:
            self.tell_time()
            return True

        if "date" in command:
            self.tell_date()
            return True

        if "system information" in command:
            self.show_system_info()
            return True

        if command.startswith("search"):
            query = command.replace(
                "search",
                "",
                1
            ).strip()

            self.search_web(query)
            return True

        self.speech.speak(
            "I am not sure how to help with that yet."
        )

        return True