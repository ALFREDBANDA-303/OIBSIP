"""
System information functions.
"""

import platform
import sys


def get_system_info():
    """Return basic computer information."""

    return {
        "Operating System": platform.system(),
        "OS Version": platform.version(),
        "Machine": platform.machine(),
        "Processor": platform.processor(),
        "Python Version": sys.version.split()[0],
    }