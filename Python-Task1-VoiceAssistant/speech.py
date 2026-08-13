"""
Speech input and text-to-speech functions.
"""

import speech_recognition as sr
import pyttsx3

from config import (
    SPEECH_RATE,
    SPEECH_VOLUME,
    LISTEN_TIMEOUT,
    PHRASE_TIME_LIMIT,
    DEFAULT_LANGUAGE,
)


class SpeechManager:
    """Manage speech recognition and text-to-speech."""

    def __init__(self):
        # Initialize text-to-speech engine
        self.engine = pyttsx3.init()

        self.engine.setProperty(
            "rate",
            SPEECH_RATE
        )

        self.engine.setProperty(
            "volume",
            SPEECH_VOLUME
        )

        # Initialize speech recognizer
        self.recognizer = sr.Recognizer()

    def speak(self, text):
        """
        Display and speak the assistant's response.

        Every response from the assistant should pass
        through this method.
        """

        print(f"Assistant: {text}")

        try:
            self.engine.say(text)
            self.engine.runAndWait()

        except Exception as error:
            print(
                f"Text-to-speech error: {error}"
            )

    def listen(self):
        """
        Listen through the microphone and convert
        speech into text.

        Returns:
            str: Recognized speech in lowercase.
            Returns an empty string when recognition fails.
        """

        try:
            with sr.Microphone() as source:

                print("\nListening...")

                # Reduce the effect of background noise.
                self.recognizer.adjust_for_ambient_noise(
                    source,
                    duration=0.8
                )

                print("Speak now...")

                audio = self.recognizer.listen(
                    source,
                    timeout=LISTEN_TIMEOUT,
                    phrase_time_limit=PHRASE_TIME_LIMIT
                )

        except OSError:
            self.speak(
                "I cannot access the microphone. "
                "Please check your microphone connection "
                "and Windows microphone permissions."
            )

            return ""

        except sr.WaitTimeoutError:
            self.speak(
                "I did not hear anything. "
                "Please try again."
            )

            return ""

        except Exception as error:
            print(
                f"Microphone error: {error}"
            )

            self.speak(
                "There was a problem accessing the microphone."
            )

            return ""

        # ---------------------------------------------------------
        # Convert speech to text
        # ---------------------------------------------------------

        try:
            print("Processing your speech...")

            command = self.recognizer.recognize_google(
                audio,
                language=DEFAULT_LANGUAGE
            )

            command = command.lower().strip()

            print(f"You: {command}")

            return command

        except sr.UnknownValueError:
            self.speak(
                "Sorry, I could not understand what you said."
            )

            return ""

        except sr.RequestError:
            self.speak(
                "The speech recognition service "
                "is unavailable right now."
            )

            return ""

        except Exception as error:
            print(
                f"Speech recognition error: {error}"
            )

            self.speak(
                "Something went wrong while processing your speech."
            )

            return ""