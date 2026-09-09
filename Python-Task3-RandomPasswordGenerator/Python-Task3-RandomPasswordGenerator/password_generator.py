"""
password_generator.py
----------------------
Core secure password generation logic.

Uses Python's `secrets` module exclusively for all randomness decisions,
since `secrets` is designed for cryptographically strong random number
generation suitable for managing secrets such as passwords. The `random`
module is intentionally never used here.
"""

import secrets

import config
from logger import log_error


class PasswordGenerationError(ValueError):
    """Raised when a password cannot be generated due to invalid input."""


class PasswordGenerator:
    """
    Generates cryptographically secure random passwords based on a
    configurable set of character-type options.
    """

    def __init__(
        self,
        length: int = config.DEFAULT_PASSWORD_LENGTH,
        use_uppercase: bool = config.DEFAULT_USE_UPPERCASE,
        use_lowercase: bool = config.DEFAULT_USE_LOWERCASE,
        use_numbers: bool = config.DEFAULT_USE_NUMBERS,
        use_special: bool = config.DEFAULT_USE_SPECIAL,
    ):
        """
        Initialize a PasswordGenerator with the requested options.

        Args:
            length: Desired password length.
            use_uppercase: Whether to include uppercase letters.
            use_lowercase: Whether to include lowercase letters.
            use_numbers: Whether to include digits.
            use_special: Whether to include special characters.

        Raises:
            PasswordGenerationError: If the configuration is invalid.
        """
        self.length = length
        self.use_uppercase = use_uppercase
        self.use_lowercase = use_lowercase
        self.use_numbers = use_numbers
        self.use_special = use_special

        self._validate_options()

    # ------------------------------------------------------------------
    # Validation
    # ------------------------------------------------------------------
    def _validate_options(self) -> None:
        """
        Validate the length and character-set selection.

        Raises:
            PasswordGenerationError: If length is out of bounds, not an
                integer, or if no character sets have been selected.
        """
        if not isinstance(self.length, int) or isinstance(self.length, bool):
            log_error("Invalid password length type provided.")
            raise PasswordGenerationError("Password length must be an integer.")

        if self.length < config.MIN_PASSWORD_LENGTH or self.length > config.MAX_PASSWORD_LENGTH:
            log_error(f"Password length out of bounds: {self.length}")
            raise PasswordGenerationError(
                f"Password length must be between {config.MIN_PASSWORD_LENGTH} "
                f"and {config.MAX_PASSWORD_LENGTH}."
            )

        if not any(
            [self.use_uppercase, self.use_lowercase, self.use_numbers, self.use_special]
        ):
            log_error("No character sets selected for password generation.")
            raise PasswordGenerationError(
                "At least one character set (uppercase, lowercase, numbers, "
                "special) must be selected."
            )

        required_sets = sum(
            [self.use_uppercase, self.use_lowercase, self.use_numbers, self.use_special]
        )
        if self.length < required_sets:
            # Impossible to guarantee at least one character from each
            # selected set if the password is shorter than the number of
            # selected sets.
            log_error(
                "Password length too short to satisfy all selected character sets."
            )
            raise PasswordGenerationError(
                f"Password length ({self.length}) is too short to include at "
                f"least one character from each of the {required_sets} selected "
                "character sets."
            )

    def _build_charset_pools(self) -> list:
        """
        Build the list of character pools that are active based on the
        current options.

        Returns:
            A list of strings, each representing one selected character
            pool (e.g. lowercase letters, digits, etc.).
        """
        pools = []
        if self.use_lowercase:
            pools.append(config.LOWERCASE_CHARS)
        if self.use_uppercase:
            pools.append(config.UPPERCASE_CHARS)
        if self.use_numbers:
            pools.append(config.NUMBER_CHARS)
        if self.use_special:
            pools.append(config.SPECIAL_CHARS)
        return pools

    # ------------------------------------------------------------------
    # Generation
    # ------------------------------------------------------------------
    def generate(self) -> str:
        """
        Generate a single secure password based on the configured options.

        The algorithm guarantees that at least one character from each
        selected character set is present, then fills the remainder of the
        password length with random characters drawn from the combined
        pool, and finally shuffles the result using a cryptographically
        secure shuffle so that the guaranteed characters are not always in
        predictable positions.

        Returns:
            The generated password string.
        """
        pools = self._build_charset_pools()
        combined_pool = "".join(pools)

        # Step 1: guarantee at least one character from each selected pool.
        password_chars = [secrets.choice(pool) for pool in pools]

        # Step 2: fill the rest of the password length from the combined pool.
        remaining = self.length - len(password_chars)
        password_chars.extend(secrets.choice(combined_pool) for _ in range(remaining))

        # Step 3: securely shuffle to avoid predictable positioning of the
        # guaranteed characters (Fisher-Yates shuffle using secrets).
        for i in range(len(password_chars) - 1, 0, -1):
            j = secrets.randbelow(i + 1)
            password_chars[i], password_chars[j] = password_chars[j], password_chars[i]

        return "".join(password_chars)

    def generate_multiple(self, count: int) -> list:
        """
        Generate multiple unique passwords.

        Args:
            count: The number of passwords to generate.

        Returns:
            A list of unique generated password strings.

        Raises:
            PasswordGenerationError: If count is invalid.
        """
        if not isinstance(count, int) or isinstance(count, bool) or count < 1:
            raise PasswordGenerationError("Count must be a positive integer.")
        if count > config.MAX_COUNT:
            raise PasswordGenerationError(
                f"Count cannot exceed {config.MAX_COUNT} passwords per request."
            )

        passwords = set()
        # Safety cap on attempts to avoid a near-infinite loop in the rare
        # case of extremely small search spaces (e.g. very short passwords).
        max_attempts = count * 20 + 50
        attempts = 0
        while len(passwords) < count and attempts < max_attempts:
            passwords.add(self.generate())
            attempts += 1

        if len(passwords) < count:
            log_error(
                "Could not generate the requested number of unique passwords "
                "given the current settings."
            )
            raise PasswordGenerationError(
                "Unable to generate the requested number of unique passwords "
                "with the current length/character settings. Try increasing "
                "the password length."
            )

        return list(passwords)
