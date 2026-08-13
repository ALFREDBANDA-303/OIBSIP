"""
Professional Voice Assistant
Oasis Infobyte Python Programming Internship
Level 3, Task 1

Author: Alfred Banda
"""

from config import USER_NAME
from speech import SpeechManager
from commands import CommandProcessor


def main():
    """Start the Voice Assistant."""

    speech = SpeechManager()

    commands = CommandProcessor(
        speech,
        USER_NAME
    )

    speech.speak(
        f"Hello {USER_NAME}. "
        "I am your voice assistant. "
        "How can I help you?"
    )

    running = True

    while running:
        try:
            command = speech.listen()
            running = commands.process(command)

        except KeyboardInterrupt:
            speech.speak(
                "Shutting down. Goodbye!"
            )
            break

        except Exception as error:
            print(
                f"Unexpected error: {error}"
            )

            speech.speak(
                "Something went wrong. "
                "Let's try again."
            )


if __name__ == "__main__":
    main()