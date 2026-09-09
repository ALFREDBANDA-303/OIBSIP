"""
main.py
-------
Command-line entry point for the Random Password Generator.

Supports generating one or more secure passwords with configurable
character sets, displaying strength analysis, viewing/clearing password
history, and launching the graphical interface.

Examples:
    python main.py --length 16 --count 3
    python main.py --length 20 --no-special --strength
    python main.py --history
    python main.py --clear-history
    python main.py --gui
"""

import argparse
import sys

import config
from password_generator import PasswordGenerator, PasswordGenerationError
from password_strength import PasswordStrengthAnalyzer
from password_history import PasswordHistoryManager
from clipboard_manager import copy_to_clipboard, is_clipboard_available
from logger import log_startup, log_shutdown, log_password_generated, log_error


def build_arg_parser() -> argparse.ArgumentParser:
    """
    Build and return the CLI argument parser.

    Returns:
        A configured argparse.ArgumentParser instance.
    """
    parser = argparse.ArgumentParser(
        prog="main.py",
        description=(
            "Random Password Generator - a secure command-line and GUI "
            "password generation tool built with Python's `secrets` module."
        ),
        formatter_class=argparse.ArgumentDefaultsHelpFormatter,
        epilog=(
            "Examples:\n"
            "  python main.py --length 16 --count 3\n"
            "  python main.py --length 20 --no-special --strength\n"
            "  python main.py --history\n"
            "  python main.py --clear-history\n"
            "  python main.py --gui\n"
        ),
    )

    parser.add_argument(
        "--length",
        type=int,
        default=config.DEFAULT_PASSWORD_LENGTH,
        help=f"Password length ({config.MIN_PASSWORD_LENGTH}-{config.MAX_PASSWORD_LENGTH}).",
    )
    parser.add_argument(
        "--count",
        type=int,
        default=config.DEFAULT_COUNT,
        help="Number of passwords to generate.",
    )

    # Character-set toggles. Each option defaults to True; the --no-* flag
    # disables it. This mirrors typical CLI ergonomics for boolean flags.
    parser.add_argument(
        "--no-uppercase",
        dest="uppercase",
        action="store_false",
        help="Exclude uppercase letters.",
    )
    parser.add_argument(
        "--no-lowercase",
        dest="lowercase",
        action="store_false",
        help="Exclude lowercase letters.",
    )
    parser.add_argument(
        "--no-numbers",
        dest="numbers",
        action="store_false",
        help="Exclude numbers.",
    )
    parser.add_argument(
        "--no-special",
        dest="special",
        action="store_false",
        help="Exclude special characters.",
    )
    parser.set_defaults(uppercase=True, lowercase=True, numbers=True, special=True)

    parser.add_argument(
        "--strength",
        action="store_true",
        help="Display strength analysis for each generated password.",
    )
    parser.add_argument(
        "--copy",
        action="store_true",
        help="Copy the generated password to the clipboard (single password only).",
    )
    parser.add_argument(
        "--save-history",
        action="store_true",
        help="Save generated password metadata to history (password text is not stored).",
    )
    parser.add_argument(
        "--history",
        action="store_true",
        help="Display saved password history and exit.",
    )
    parser.add_argument(
        "--clear-history",
        action="store_true",
        help="Clear all saved password history and exit.",
    )
    parser.add_argument(
        "--gui",
        action="store_true",
        help="Launch the graphical user interface instead of the CLI.",
    )

    return parser


def handle_history_view() -> int:
    """Print all stored password history entries."""
    manager = PasswordHistoryManager()
    entries = manager.get_history()
    if not entries:
        print("No password history found.")
        return 0

    print(f"Password History ({len(entries)} entries):")
    print("-" * 60)
    for i, entry in enumerate(entries, start=1):
        print(
            f"{i:>3}. {entry.get('timestamp', 'unknown time')} | "
            f"length={entry.get('length', '?')} | "
            f"strength={entry.get('strength', '?')}"
        )
    return 0


def handle_history_clear() -> int:
    """Clear all stored password history entries."""
    manager = PasswordHistoryManager()
    manager.clear_history()
    print("Password history cleared.")
    return 0


def handle_generate(args: argparse.Namespace) -> int:
    """
    Generate one or more passwords according to CLI arguments and print
    them, along with optional strength analysis, clipboard copy, and
    history saving.

    Returns:
        Process exit code (0 for success, 1 for failure).
    """
    try:
        generator = PasswordGenerator(
            length=args.length,
            use_uppercase=args.uppercase,
            use_lowercase=args.lowercase,
            use_numbers=args.numbers,
            use_special=args.special,
        )
        passwords = generator.generate_multiple(args.count)
    except PasswordGenerationError as exc:
        print(f"Error: {exc}", file=sys.stderr)
        return 1

    history_manager = PasswordHistoryManager() if args.save_history else None
    last_strength = None

    for i, pw in enumerate(passwords, start=1):
        print(f"[{i}] {pw}")

        strength_label = None
        if args.strength or args.save_history:
            result = PasswordStrengthAnalyzer.analyze(pw)
            strength_label = result.rating
            if args.strength:
                print(f"    Strength: {result.rating} (score {result.score}/7)")
                for tip in result.feedback:
                    print(f"      - {tip}")

        if history_manager is not None:
            history_manager.add_entry(length=len(pw), strength=strength_label or "Unknown")

        last_strength = strength_label

    log_password_generated(
        length=args.length, count=len(passwords), strength=last_strength or "Not analyzed"
    )

    if args.copy:
        if len(passwords) != 1:
            print(
                "Note: --copy only applies when exactly one password is generated; skipping.",
                file=sys.stderr,
            )
        elif not is_clipboard_available():
            print(
                "Warning: No clipboard mechanism detected on this system; "
                "could not copy password.",
                file=sys.stderr,
            )
        else:
            success = copy_to_clipboard(passwords[0])
            if success:
                print("Password copied to clipboard.")
            else:
                print("Warning: Failed to copy password to clipboard.", file=sys.stderr)

    return 0


def main(argv=None) -> int:
    """
    Main CLI entry point.

    Args:
        argv: Optional list of arguments (used for testing); defaults to
            sys.argv when None.

    Returns:
        Process exit code.
    """
    log_startup()
    parser = build_arg_parser()
    args = parser.parse_args(argv)

    exit_code = 0
    try:
        if args.gui:
            from gui import launch_gui

            launch_gui()
        elif args.history:
            exit_code = handle_history_view()
        elif args.clear_history:
            exit_code = handle_history_clear()
        else:
            exit_code = handle_generate(args)
    except Exception as exc:  # top-level safety net for graceful CLI errors
        log_error(f"Unhandled error in CLI: {exc}")
        print(f"An unexpected error occurred: {exc}", file=sys.stderr)
        exit_code = 1
    finally:
        log_shutdown()

    return exit_code


if __name__ == "__main__":
    sys.exit(main())
