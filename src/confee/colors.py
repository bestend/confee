"""ANSI color codes and terminal styling utilities."""

import os
from typing import Optional


class Color:
    """ANSI color code management with global enable/disable support.

    Examples:
        >>> print(f"{Color.BOLD}Bold Text{Color.RESET}")
        >>> Color.enable(False)  # Disable colors globally
        >>> Color.styled("Hello", Color.RED)  # Returns unstyled text
    """

    # Reset and style codes
    RESET = "\033[0m"
    BOLD = "\033[1m"
    DIM = "\033[2m"
    ITALIC = "\033[3m"
    UNDERLINE = "\033[4m"

    # Foreground colors
    BLACK = "\033[30m"
    RED = "\033[31m"
    GREEN = "\033[32m"
    YELLOW = "\033[33m"
    BLUE = "\033[34m"
    MAGENTA = "\033[35m"
    CYAN = "\033[36m"
    WHITE = "\033[37m"

    # Bright colors
    BRIGHT_BLACK = "\033[90m"
    BRIGHT_RED = "\033[91m"
    BRIGHT_GREEN = "\033[92m"
    BRIGHT_YELLOW = "\033[93m"
    BRIGHT_BLUE = "\033[94m"
    BRIGHT_MAGENTA = "\033[95m"
    BRIGHT_CYAN = "\033[96m"
    BRIGHT_WHITE = "\033[97m"

    # Background colors
    BG_BLACK = "\033[40m"
    BG_RED = "\033[41m"
    BG_GREEN = "\033[42m"
    BG_YELLOW = "\033[43m"
    BG_BLUE = "\033[44m"
    BG_MAGENTA = "\033[45m"
    BG_CYAN = "\033[46m"
    BG_WHITE = "\033[47m"

    _enabled: bool = True

    @classmethod
    def enable(cls, enabled: bool) -> None:
        """Enable/disable ANSI color output globally.

        Args:
            enabled: Whether to enable color output
        """
        cls._enabled = enabled

    @classmethod
    def is_enabled(cls) -> bool:
        """Check if color output is currently enabled."""
        return cls._enabled

    @classmethod
    def auto_detect(cls) -> None:
        """Auto-detect color support based on environment.

        Disables color if:
        - NO_COLOR environment variable is set
        - TERM is 'dumb'
        - Not running in a TTY
        """
        import sys

        no_color = os.getenv("NO_COLOR") or os.getenv("CONFEE_NO_COLOR")
        dumb_term = os.getenv("TERM") == "dumb"
        is_tty = hasattr(sys.stdout, "isatty") and sys.stdout.isatty()

        cls._enabled = not (no_color or dumb_term or not is_tty)

    @classmethod
    def _maybe(cls, code: str) -> str:
        """Return color code if enabled, empty string otherwise."""
        return code if cls._enabled else ""

    @classmethod
    def styled(cls, text: str, *styles: str) -> str:
        """Apply styles to text if colors are enabled.

        Args:
            text: Text to style
            *styles: Style codes to apply

        Returns:
            Styled text or plain text if colors disabled

        Examples:
            >>> Color.styled("Error", Color.RED, Color.BOLD)
            '\\033[31m\\033[1mError\\033[0m'
        """
        if not cls._enabled or not styles:
            return text
        style_codes = "".join(styles)
        return f"{style_codes}{text}{cls.RESET}"

    @classmethod
    def success(cls, text: str) -> str:
        """Style text as success (green)."""
        return cls.styled(text, cls.BRIGHT_GREEN)

    @classmethod
    def error(cls, text: str) -> str:
        """Style text as error (red)."""
        return cls.styled(text, cls.RED)

    @classmethod
    def warning(cls, text: str) -> str:
        """Style text as warning (yellow)."""
        return cls.styled(text, cls.BRIGHT_YELLOW)

    @classmethod
    def info(cls, text: str) -> str:
        """Style text as info (cyan)."""
        return cls.styled(text, cls.CYAN)

    @classmethod
    def highlight(cls, text: str) -> str:
        """Style text as highlighted (bold)."""
        return cls.styled(text, cls.BOLD)

    @classmethod
    def dim(cls, text: str) -> str:
        """Style text as dimmed."""
        return cls.styled(text, cls.DIM)


class ProgressIndicator:
    """Simple progress indicator for long operations.

    Examples:
        >>> with ProgressIndicator("Loading config"):
        ...     load_config()
        Loading config... done
    """

    def __init__(self, message: str, show_spinner: bool = False):
        """Initialize progress indicator.

        Args:
            message: Message to display
            show_spinner: Whether to show a spinner (future feature)
        """
        self.message = message
        self.show_spinner = show_spinner

    def __enter__(self) -> "ProgressIndicator":
        """Start progress indicator."""
        import sys

        if Color.is_enabled():
            sys.stdout.write(f"{Color.DIM}{self.message}...{Color.RESET} ")
            sys.stdout.flush()
        return self

    def __exit__(
        self,
        exc_type: Optional[type],
        exc_val: Optional[Exception],
        exc_tb: Optional[object],
    ) -> None:
        """End progress indicator."""
        import sys

        if exc_type is not None:
            print(Color.error("failed"))
        else:
            print(Color.success("done"))
