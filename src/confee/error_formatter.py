"""User-friendly error formatting for validation errors."""

import re
from typing import Any, Dict, List, Optional

from .colors import Color


class ErrorFormatter:
    """Format validation errors in a user-friendly way.

    Supports compact and verbose output styles with colorized output.

    Examples:
        >>> try:
        ...     config = AppConfig(**data)
        ... except ValidationError as e:
        ...     print(ErrorFormatter.format_validation_error(e))
    """

    @staticmethod
    def format_validation_error(error: Exception, style: str = "compact") -> str:
        """Format Pydantic validation errors in a readable way.

        Args:
            error: Pydantic ValidationError or any exception
            style: Output style - "compact" or "verbose"

        Returns:
            Formatted error message
        """
        from pydantic import ValidationError

        error_str = str(error)

        # Handle Pydantic ValidationError with rich information
        if isinstance(error, ValidationError):
            errors = error.errors()
            return ErrorFormatter._format_pydantic_errors(errors, style)

        # Handle string-based validation errors (legacy format)
        if "validation error" in error_str.lower():
            return ErrorFormatter._format_string_error(error_str, style)

        # Generic error formatting
        if style == "compact":
            return f"Error: {error_str}"
        return f"{Color.RED}Error: {error_str}{Color.RESET}"

    @staticmethod
    def _format_pydantic_errors(errors: List[Dict[str, Any]], style: str) -> str:
        """Format Pydantic V2 validation errors.

        Args:
            errors: List of error dictionaries from ValidationError.errors()
            style: Output style

        Returns:
            Formatted error string
        """
        if style == "compact":
            return ErrorFormatter._format_compact_errors(errors)
        return ErrorFormatter._format_verbose_errors(errors)

    @staticmethod
    def _format_compact_errors(errors: List[Dict[str, Any]]) -> str:
        """Format errors in compact single-line style."""
        if not errors:
            return "Config error: validation failed"

        first_error = errors[0]
        loc = first_error.get("loc", ("unknown",))
        field = ".".join(str(p) for p in loc) if loc else "unknown"
        error_type = first_error.get("type", "unknown_error")
        msg = first_error.get("msg", "validation failed")

        if error_type == "missing":
            return f"Config error: missing required field '{field}'"
        return f"Config error: field '{field}' - {msg}"

    @staticmethod
    def _format_verbose_errors(errors: List[Dict[str, Any]]) -> str:
        """Format errors in verbose multi-line style with colors."""
        lines = []
        lines.append(f"{Color.BOLD}{Color.RED}❌ Configuration Validation Error{Color.RESET}")
        lines.append("")

        if errors:
            lines.append(
                f"  {Color.BRIGHT_YELLOW}Found {len(errors)} validation error(s):{Color.RESET}"
            )
            lines.append("")

            for idx, error_detail in enumerate(errors, 1):
                lines.extend(ErrorFormatter._format_single_error(idx, error_detail))
        else:
            lines.append("  Validation failed (no details available)")
            lines.append("")

        lines.extend(ErrorFormatter._get_fix_suggestions())

        return "\n".join(lines)

    @staticmethod
    def _format_single_error(idx: int, error_detail: Dict[str, Any]) -> List[str]:
        """Format a single error detail."""
        lines = []

        loc = error_detail.get("loc", ("unknown",))
        field = ".".join(str(p) for p in loc) if loc else "unknown"
        error_type = error_detail.get("type", "unknown_error")
        msg = error_detail.get("msg", "validation failed")
        input_value = error_detail.get("input", None)

        lines.append(f"  {Color.BRIGHT_MAGENTA}[{idx}] Field: {Color.BOLD}{field}{Color.RESET}")
        lines.append(f"      {Color.YELLOW}Error: {msg}{Color.RESET}")
        lines.append(f"      {Color.DIM}Type: {error_type}{Color.RESET}")

        if input_value is not None:
            lines.append(f"      {Color.DIM}Got: {repr(input_value)}{Color.RESET}")

        lines.append("")

        return lines

    @staticmethod
    def _format_string_error(error_str: str, style: str) -> str:
        """Format errors from string representation."""
        if style == "compact":
            # Try to extract field name
            if "field required" in error_str.lower():
                match = re.search(r"(\w+)\s*\n\s*Field required", error_str)
                if match:
                    return f"Config error: missing required field '{match.group(1)}'"
            return "Config error: validation failed"

        # Verbose format
        lines = []
        lines.append(f"{Color.BOLD}{Color.RED}❌ Configuration Validation Error{Color.RESET}")
        lines.append("")

        if "field required" in error_str.lower():
            match = re.search(r"(\w+)\s*\n\s*Field required", error_str)
            if match:
                field_name = match.group(1)
                lines.append(
                    f"  {Color.BRIGHT_YELLOW}Missing required field: "
                    f"{Color.BOLD}{field_name}{Color.RESET}"
                )
                lines.append("  This field is required for configuration.")
            else:
                lines.append("  A required field is missing.")
        else:
            lines.append(f"  {error_str}")

        lines.append("")
        lines.extend(ErrorFormatter._get_fix_suggestions())

        return "\n".join(lines)

    @staticmethod
    def _get_fix_suggestions() -> List[str]:
        """Get common fix suggestions."""
        return [
            f"  {Color.CYAN}💡 How to fix:{Color.RESET}",
            "    1. Add the required field to your configuration file",
            "    2. Or pass the value via CLI: python main.py name=myapp",
            "    3. Or set an environment variable: export CONFEE_NAME=myapp",
            "    4. Check field types match your configuration class",
        ]


class FieldErrorDetail:
    """Structured representation of a field validation error."""

    def __init__(
        self,
        field: str,
        error_type: str,
        message: str,
        input_value: Optional[Any] = None,
        context: Optional[Dict[str, Any]] = None,
    ):
        """Initialize error detail.

        Args:
            field: Field name (can be dot-notation for nested)
            error_type: Type of error (e.g., 'missing', 'type_error')
            message: Human-readable error message
            input_value: The invalid input value (if any)
            context: Additional error context
        """
        self.field = field
        self.error_type = error_type
        self.message = message
        self.input_value = input_value
        self.context = context or {}

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary representation."""
        return {
            "field": self.field,
            "error_type": self.error_type,
            "message": self.message,
            "input_value": self.input_value,
            "context": self.context,
        }

    def __repr__(self) -> str:
        return f"FieldErrorDetail(field={self.field!r}, error_type={self.error_type!r})"
