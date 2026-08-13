"""
Application launcher for the Voice Assistant.
"""

import subprocess


class ApplicationLauncher:
    """Launch supported applications on Windows."""

    def __init__(self, speech_manager):
        self.speech = speech_manager

        self.applications = {
            "notepad": "notepad.exe",
            "calculator": "calc.exe",
            "paint": "mspaint.exe",
            "command prompt": "cmd.exe",
            "cmd": "cmd.exe",
        }

    def launch(self, application):
        """Launch a supported application."""

        application = application.lower().strip()

        if application not in self.applications:
            self.speech.speak(
                f"I do not know how to open {application} yet."
            )
            return

        program = self.applications[application]

        self.speech.speak(
            f"Opening {application}."
        )

        try:
            subprocess.Popen(program)

        except Exception:
            self.speech.speak(
                f"I could not open {application}."
            )