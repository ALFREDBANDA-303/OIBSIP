"""
Command processing for the Voice Assistant.
"""

import ast
import datetime
import operator
import webbrowser

from system_info import get_system_info
from app_launcher import ApplicationLauncher
from weather import WeatherService


class CommandProcessor:
    """Process commands received by the Voice Assistant."""

    def __init__(self, speech_manager, user_name):
        self.speech = speech_manager
        self.user_name = user_name

        # Application launcher
        self.app_launcher = ApplicationLauncher(
            speech_manager
        )

        # Weather service
        self.weather = WeatherService(
            speech_manager
        )

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
        """Search the web using the default browser."""

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

        try:
            webbrowser.open(url)

        except Exception:
            self.speech.speak(
                "I could not open the web browser."
            )

    def show_system_info(self):
        """Read basic system information."""

        try:
            information = get_system_info()

            self.speech.speak(
                f"You are using "
                f"{information['Operating System']}."
            )

            self.speech.speak(
                f"Your Python version is "
                f"{information['Python Version']}."
            )

        except Exception:
            self.speech.speak(
                "I could not retrieve the system information."
            )

    def calculate(self, expression):
        """Safely calculate a mathematical expression."""

        if not expression:
            self.speech.speak(
                "Please tell me the calculation."
            )
            return

        operators = {
            ast.Add: operator.add,
            ast.Sub: operator.sub,
            ast.Mult: operator.mul,
            ast.Div: operator.truediv,
            ast.Pow: operator.pow,
            ast.Mod: operator.mod,
        }

        def evaluate(node):
            """Safely evaluate a mathematical expression."""

            if isinstance(node, ast.Constant):
                if isinstance(node.value, (int, float)):
                    return node.value

                raise ValueError("Invalid number.")

            if isinstance(node, ast.BinOp):
                operation = operators.get(
                    type(node.op)
                )

                if operation is None:
                    raise ValueError(
                        "Unsupported operation."
                    )

                return operation(
                    evaluate(node.left),
                    evaluate(node.right)
                )

            if isinstance(node, ast.UnaryOp):

                if isinstance(node.op, ast.USub):
                    return -evaluate(node.operand)

                if isinstance(node.op, ast.UAdd):
                    return evaluate(node.operand)

            raise ValueError(
                "Invalid mathematical expression."
            )

        try:
            tree = ast.parse(
                expression,
                mode="eval"
            )

            result = evaluate(tree.body)

            if isinstance(result, float) and result.is_integer():
                result = int(result)

            self.speech.speak(
                f"The answer is {result}."
            )

        except ZeroDivisionError:
            self.speech.speak(
                "You cannot divide by zero."
            )

        except (ValueError, SyntaxError):
            self.speech.speak(
                "I could not calculate that expression."
            )

        except Exception:
            self.speech.speak(
                "An error occurred while calculating."
            )

    def get_weather(self, command):
        """Process a weather command."""

        city = command.strip()

        if city.startswith("weather"):
            city = city.replace(
                "weather",
                "",
                1
            ).strip()

        if city.startswith("in "):
            city = city.replace(
                "in ",
                "",
                1
            ).strip()

        if city.startswith("for "):
            city = city.replace(
                "for ",
                "",
                1
            ).strip()

        if not city:
            self.speech.speak(
                "Please tell me the city."
            )
            return

        self.weather.get_weather(city)

    def process(self, command):
        """
        Process a recognized command.

        Returns:
            False when the assistant should stop.
            True when the assistant should continue.
        """

        if not command:
            return True

        command = command.lower().strip()

        # ---------------------------------------------------------------
        # Exit commands
        # ---------------------------------------------------------------

        if any(
            word in command
            for word in [
                "goodbye",
                "exit",
                "quit",
                "stop",
                "shutdown",
            ]
        ):
            self.speech.speak(
                f"Goodbye, {self.user_name}. "
                "Have a great day!"
            )

            return False

        # ---------------------------------------------------------------
        # Greetings
        # ---------------------------------------------------------------

        if any(
            command == word
            or command.startswith(word + " ")
            for word in [
                "hello",
                "hi",
                "hey",
            ]
        ):
            self.speech.speak(
                f"Hello {self.user_name}. "
                "How can I help you?"
            )

            return True

        # ---------------------------------------------------------------
        # Weather
        # ---------------------------------------------------------------

        if (
            command.startswith("weather")
            or command.startswith("what is the weather")
            or command.startswith("what's the weather")
        ):
            weather_command = command

            weather_command = weather_command.replace(
                "what is the weather",
                "weather",
                1
            )

            weather_command = weather_command.replace(
                "what's the weather",
                "weather",
                1
            )

            self.get_weather(weather_command)

            return True

        # ---------------------------------------------------------------
        # Time
        # ---------------------------------------------------------------

        if "time" in command:
            self.tell_time()
            return True

        # ---------------------------------------------------------------
        # Date
        # ---------------------------------------------------------------

        if "date" in command:
            self.tell_date()
            return True

        # ---------------------------------------------------------------
        # System information
        # ---------------------------------------------------------------

        if (
            "system information" in command
            or "system info" in command
            or "computer information" in command
        ):
            self.show_system_info()
            return True

        # ---------------------------------------------------------------
        # Calculator
        # ---------------------------------------------------------------

        if command.startswith("calculate"):
            expression = command.replace(
                "calculate",
                "",
                1
            ).strip()

            self.calculate(expression)

            return True

        # ---------------------------------------------------------------
        # Web search
        # ---------------------------------------------------------------

        if command.startswith("search"):
            query = command.replace(
                "search",
                "",
                1
            ).strip()

            self.search_web(query)

            return True

        # ---------------------------------------------------------------
        # Application launcher
        # ---------------------------------------------------------------

        if command.startswith("open "):

            application = command.replace(
                "open ",
                "",
                1
            ).strip()

            self.app_launcher.launch(
                application
            )

            return True

        # ---------------------------------------------------------------
        # Unsupported command
        # ---------------------------------------------------------------

        self.speech.speak(
            "I am not sure how to help with that yet."
        )

        return True