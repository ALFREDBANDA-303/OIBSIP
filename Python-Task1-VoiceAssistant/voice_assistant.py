"""
Voice Assistant
Oasis Infobyte Python Programming Internship - Task 1

A simple voice-controlled assistant that listens through the microphone,
converts speech to text, performs a small set of useful tasks, and replies
back using text-to-speech.

Author: Alfred Banda
"""

import datetime
import webbrowser

import speech_recognition as sr
import pyttsx3

print("Voice Assistant file started")

# ---------------------------------------------------------------------------
# Configuration
# ---------------------------------------------------------------------------

USER_NAME = "Alfred"

# Text-to-speech engine is created once and reused throughout the program.
engine = pyttsx3.init()
engine.setProperty("rate", 175)     # Speaking speed (words per minute)
engine.setProperty("volume", 1.0)   # Volume level: 0.0 (silent) to 1.0 (max)

# Recognizer is created once and reused throughout the program.
recognizer = sr.Recognizer()


# ---------------------------------------------------------------------------
# Core functions
# ---------------------------------------------------------------------------

def speak(text):
    """Speak the given text out loud and print it for reference."""
    print(f"Assistant: {text}")
    engine.say(text)
    engine.runAndWait()


def listen():
    """
    Listen to the microphone and convert the captured speech into text.

    Returns:
        str: The recognized command in lowercase, or an empty string if
             nothing usable was recognized.
    """
    try:
        with sr.Microphone() as source:
            print("\nListening...")
            # Adjust for ambient/background noise before capturing audio.
            recognizer.adjust_for_ambient_noise(source, duration=0.8)
            audio = recognizer.listen(source, timeout=6, phrase_time_limit=8)
    except OSError:
        # Raised when no microphone is found or it cannot be accessed.
        speak("I can't access the microphone. Please check your audio device.")
        return ""
    except sr.WaitTimeoutError:
        # No speech detected within the timeout window.
        speak("I didn't hear anything. Please try again.")
        return ""

    try:
        command = recognizer.recognize_google(audio)
        command = command.lower().strip()
        print(f"You said: {command}")
        return command
    except sr.UnknownValueError:
        # Speech was captured but could not be understood.
        speak("Sorry, I couldn't understand that. Could you repeat it?")
        return ""
    except sr.RequestError:
        # The speech recognition service is unreachable or failed.
        speak("The speech recognition service isn't available right now.")
        return ""


def tell_time():
    """Speak the current system time."""
    current_time = datetime.datetime.now().strftime("%I:%M %p")
    speak(f"The current time is {current_time}.")


def tell_date():
    """Speak the current system date."""
    current_date = datetime.datetime.now().strftime("%B %d, %Y")
    speak(f"Today's date is {current_date}.")


def search_web(query):
    """
    Open the default web browser and search for the given query.

    Args:
        query (str): The topic to search for.
    """
    if not query:
        speak("You didn't tell me what to search for.")
        return

    speak(f"Searching for {query}.")
    url = f"https://www.google.com/search?q={query}"
    webbrowser.open(url)


# ---------------------------------------------------------------------------
# Command processing
# ---------------------------------------------------------------------------

def process_command(command):
    """
    Decide which action to take based on the recognized command.

    Args:
        command (str): The lowercase text of the user's spoken command.

    Returns:
        bool: False if the assistant should stop running, True otherwise.
    """
    if not command:
        # Empty or unrecognized command; nothing to do this round.
        return True

    # --- Exit commands ---
    if any(word in command for word in ["goodbye", "exit", "quit", "stop"]):
        speak(f"Goodbye, {USER_NAME}. Have a great day!")
        return False

    # --- Greetings ---
    if any(word in command for word in ["hello", "hi", "hey"]):
        speak(f"Hello {USER_NAME}. How can I help you?")
        return True

    # --- Time ---
    if "time" in command:
        tell_time()
        return True

    # --- Date ---
    if "date" in command:
        tell_date()
        return True

    # --- Web search ---
    if command.startswith("search"):
        query = command.replace("search", "", 1).strip()
        search_web(query)
        return True

    # --- Unsupported command ---
    speak("I'm not sure how to help with that yet.")
    return True


# ---------------------------------------------------------------------------
# Main program loop
# ---------------------------------------------------------------------------

def main():
    """Run the voice assistant's main conversation loop."""
    speak(f"Hello {USER_NAME}, I'm your voice assistant. How can I help you?")

    running = True
    while running:
        try:
            command = listen()
            running = process_command(command)
        except KeyboardInterrupt:
            speak("Shutting down. Goodbye!")
            break
        except Exception as error:
            # Catch-all so an unexpected issue doesn't crash the program.
            print(f"Unexpected error: {error}")
            speak("Something went wrong. Let's try that again.")


if __name__ == "__main__":
    main()
