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
        self.engine = pyttsx3.init()
        self.engine.setProperty("rate", SPEECH_RATE)
        self.engine.setProperty("volume", SPEECH_VOLUME)

        self.recognizer = sr.Recognizer()

    def speak(self, text):
        """Speak text and display it in the terminal."""
        print(f"Assistant: {text}")

        self.engine.say(text)
        self.engine.runAndWait()

    def listen(self):
        """Listen to the microphone and return recognized speech."""

        try:
            with sr.Microphone() as source:
                print("\nListening...")

                self.recognizer.adjust_for_ambient_noise(
                    source,
                    duration=0.8
                )

                audio = self.recognizer.listen(
                    source,
                    timeout=LISTEN_TIMEOUT,
                    phrase_time_limit=PHRASE_TIME_LIMIT
                )

        except OSError:
            self.speak(
                "I cannot access the microphone. "
                "Please check your audio device."
            )
            return ""

        except sr.WaitTimeoutError:
            self.speak("I did not hear anything. Please try again.")
            return ""

        try:
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
                "The speech recognition service is unavailable."
            )
            return ""