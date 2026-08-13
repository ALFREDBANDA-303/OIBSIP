# Python Task 1: Voice Assistant

**Internship:** Oasis Infobyte Python Programming Internship
**Task:** Task 1 — Voice Assistant
**Level:** Level 3
**Author:** Alfred Banda

## Project Overview

This project is a Python-based Voice Assistant developed as Task 1 of the
Oasis Infobyte Python Programming Internship.

The assistant accepts voice commands through the computer microphone,
converts speech into text, processes the command, performs the requested
operation, and provides a spoken response using text-to-speech.

The project is being built incrementally. The core voice system is complete
and working; several additional features are planned and will be added as
separate modules. The sections below are split into **Implemented Features**
and **Planned Features** so the README always reflects what actually runs
today.

## Objectives

- Build a functional voice-controlled assistant using Python.
- Implement speech-to-text functionality.
- Implement text-to-speech functionality.
- Process natural voice commands.
- Perform common computer tasks.
- Provide spoken responses.
- Implement error handling.
- Move toward a modular Python structure as features are added.

## Implemented Features

These features exist in the current code (`voice_assistant.py`) and have
been tested.

### 1. Voice Input
Uses the computer microphone to receive spoken commands, with background
noise adjustment before each listening session.

### 2. Speech-to-Text
Converts spoken input into text using the `SpeechRecognition` library
(Google speech recognition backend).

Example:
```
User speaks: "What is the time?"
Converted command: "what is the time"
```

### 3. Text-to-Speech
Responds using the computer's voice system through `pyttsx3`. Every response
is printed to the terminal and spoken aloud, with configurable rate and
volume.

### 4. Greetings
Recognizes: "Hello", "Hi", "Hey".

```
Assistant: Hello Alfred. How can I help you?
```

### 5. Time
```
User: What is the time?
Assistant: The current time is 09:30 AM.
```

### 6. Date
```
User: What is today's date?
Assistant: Today's date is August 13, 2026.
```

### 7. Web Search
Opens the default web browser and performs a Google search for the
requested topic.

```
User: Search Python programming
Assistant: Searching for Python programming.
```

### 8. Exit Commands
Recognizes: "Goodbye", "Exit", "Quit", "Stop", and ends the program with a
spoken farewell.

### 9. Error Handling
Handles, without crashing:
- Unavailable/inaccessible microphone
- No speech detected within the listening window
- Speech that could not be understood
- Speech recognition service failures

## Planned Features (In Progress / Not Yet Implemented)

The features below are part of the intended modular design but are **not
yet built or tested**. They are listed here as a roadmap, not as working
functionality. This README will be updated to move each item into
"Implemented Features" once its module is finished and tested.

| Feature | Target module |
|---|---|
| Calculator (AST-based, no `eval()`) | `commands.py` |
| Application launcher | `app_launcher.py` |
| System information (OS, Python version) | `system_info.py` |
| Weather lookup | `weather.py` |
| Knowledge search | `knowledge.py` |
| Notes storage | `notes.py` |
| Reminders | `reminders.py` |
| Command history | `history.py` |
| Logging to `logs/assistant.log` | `logger.py` |
| Externalized configuration (rate, volume, timeouts, language) | `config.py` |
| Multilingual speech recognition | `language.py` |
| Wake-word activation | — |
| Confirmation before sensitive actions | `confirmation.py` |
| Split of speech I/O and command routing into dedicated modules | `speech.py`, `commands.py` |

## Technologies Used (Current)

- Python 3.13
- `SpeechRecognition`
- `pyttsx3`
- `PyAudio`
- `datetime` (standard library)
- `webbrowser` (standard library)

Technologies expected to be added alongside the planned features above
include `requests`, `python-dotenv`, `ast`, `operator`, `json`, `logging`,
`os`, `platform`, and `subprocess`.

## Current Project Structure

```
Python-Task1-VoiceAssistant/
├── voice_assistant.py
├── README.md
└── screenshots/
```

### Target Structure (once planned modules are complete)

```
Python-Task1-VoiceAssistant/
│
├── voice_assistant.py
├── commands.py
├── speech.py
├── config.py
├── system_info.py
├── app_launcher.py
├── weather.py
├── knowledge.py
├── notes.py
├── reminders.py
├── history.py
├── logger.py
├── language.py
├── confirmation.py
├── requirements.txt
├── .env
├── .gitignore
├── README.md
│
├── data/
│   ├── notes.json
│   └── reminders.json
│
├── logs/
│   └── assistant.log
│
└── screenshots/
```

## Installation

Install the current dependencies:

```bash
pip install SpeechRecognition pyttsx3 pyaudio
```

> **Windows:** if `pyaudio` fails to install, use `pip install pipwin` then
> `pipwin install pyaudio`.
> **macOS:** run `brew install portaudio` first, then `pip install pyaudio`.
> **Linux:** install `portaudio19-dev` (or `python3-pyaudio`) before running
> `pip install pyaudio`.

Once the planned modules are added, a `requirements.txt` will be introduced
covering `requests` and `python-dotenv` as well.

## Running the Application

From the project directory:

```bash
python voice_assistant.py
```

The assistant starts, greets the user, and waits for voice input.

## Example Commands (Currently Working)

| Say | Result |
|---|---|
| "Hello" | Greeting |
| "What is the time?" | Speaks current time |
| "What is today's date?" | Speaks current date |
| "Search Python programming" | Opens browser search |
| "Goodbye" / "Exit" / "Quit" / "Stop" | Ends the program |

## Error Handling (Currently Working)

| Situation | Response |
|---|---|
| Microphone unavailable | "I can't access the microphone. Please check your audio device." |
| No speech detected | "I didn't hear anything. Please try again." |
| Speech not understood | "Sorry, I couldn't understand that. Could you repeat it?" |
| Speech recognition service unavailable | "The speech recognition service isn't available right now." |

Error handling for the calculator (invalid expression, division by zero),
browser failures, and other planned features will be documented once those
modules are implemented.

## Security Considerations (Planned)

Once implemented, the calculator will not use unrestricted Python
`eval()`. Mathematical expressions will be parsed using Python's `ast`
module, with only approved operators processed.

Configuration and environment variables (e.g. API keys for weather or
knowledge lookups) will be kept out of source code and out of version
control via `.env` and `.gitignore`.

## GitHub

Part of the OIBSIP repository:

```
OIBSIP/
│
├── Python-Task1-VoiceAssistant/
├── Python-Task2-BMICalculator/
├── Python-Task3-RandomPasswordGenerator/
├── Python-Task4-WeatherApp/
└── Python-Task5-ChatApplication/
```

Repository: https://github.com/ALFREDBANDA-303/OIBSIP

## Screenshots

Stored inside `screenshots/`. Current recommended screenshots (matching
implemented features):

- Voice Assistant startup
- Recognized voice command
- Time response
- Date response
- Web search
- Exit command

Additional screenshots (system info, calculator, weather, etc.) will be
added once those features are implemented and tested.

## Testing Checklist

**Implemented and tested:**
- [ ] Voice input
- [ ] Speech-to-text
- [ ] Text-to-speech
- [ ] Greetings
- [ ] Time
- [ ] Date
- [ ] Web search
- [ ] Exit commands
- [ ] Core error handling

**Planned, not yet built:**
- [ ] Calculator
- [ ] Application launcher
- [ ] System information
- [ ] Weather
- [ ] Knowledge search
- [ ] Notes
- [ ] Reminders
- [ ] Command history
- [ ] Logging
- [ ] Externalized configuration
- [ ] Multilingual support
- [ ] Wake-word support
- [ ] Confirmation before sensitive actions
- [ ] Full modular file split

## Development Approach

The project started as a single working script covering the core
requirements, and is being extended toward a modular structure — separating
speech handling, command routing, and individual features into their own
modules — as each new feature is completed and tested. Features are only
marked as implemented in this README once their code exists and has been
verified to work.

## Future Improvements

- More natural language processing
- More application integrations
- Offline speech recognition
- More languages
- Improved wake-word detection
- GUI interface
- User profiles
- Calendar and email integration
- Smart home integration
- Improved security controls

## Internship Information

**Project:** Oasis Infobyte Python Programming Internship
**Task:** Task 1: Voice Assistant
**Level:** Level 3

## Author

Alfred Banda
Computer Science Student / Python Developer
GitHub: https://github.com/ALFREDBANDA-303

## Project Status

The Voice Assistant currently implements the core voice interaction loop:
listening, speech-to-text, command handling for greetings/time/date/web
search/exit, text-to-speech, and error handling. Additional modules
(calculator, system info, app launcher, weather, knowledge search, notes,
reminders, history, logging, configuration, multilingual support,
wake-word, confirmation) are planned and will be added incrementally, with
this README updated as each is completed and tested.