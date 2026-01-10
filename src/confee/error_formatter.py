"""User-friendly error formatting for validation errors."""

from __future__ import annotations

import re
from typing import TYPE_CHECKING, Any, Literal

if TYPE_CHECKING:
    from pydantic_core import ErrorDetails

from .colors import Color

# Error type to user-friendly message mapping for Pydantic V2
_ERROR_TYPE_MESSAGES: dict[str, str] = {
    "missing": "required field is missing",
    "string_type": "expected a string value",
    "int_type": "expected an integer value",
    "float_type": "expected a float value",
    "bool_type": "expected a boolean value",
    "list_type": "expected a list/array value",
    "dict_type": "expected a dictionary/object value",
    "none_not_allowed": "null/None is not allowed",
    "int_parsing": "failed to parse as integer",
    "float_parsing": "failed to parse as float",
    "bool_parsing": "failed to parse as boolean",
    "string_too_short": "string is too short",
    "string_too_long": "string is too long",
    "greater_than": "value must be greater than the minimum",
    "greater_than_equal": "value must be greater than or equal to the minimum",
    "less_than": "value must be less than the maximum",
    "less_than_equal": "value must be less than or equal to the maximum",
    "literal_error": "value is not one of the allowed options",
    "enum": "value is not a valid enum member",
    "url_parsing": "invalid URL format",
    "json_invalid": "invalid JSON format",
    "value_error": "invalid value",
    "assertion_error": "assertion failed",
    "extra_forbidden": "extra fields are not permitted",
}


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
    def format_validation_error(
        error: Exception, style: Literal["compact", "verbose"] = "compact"
    ) -> str:
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
    def _format_pydantic_errors(
        errors: list[ErrorDetails], style: Literal["compact", "verbose"]
    ) -> str:
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
    def _format_compact_errors(errors: list[ErrorDetails]) -> str:
        if not errors:
            return "Config error: validation failed"

        first_error = errors[0]
        loc = first_error.get("loc", ("unknown",))
        field = ".".join(str(p) for p in loc) if loc else "unknown"
        error_type = first_error.get("type", "unknown_error")
        msg = first_error.get("msg", "validation failed")

        if error_type == "missing":
            return f"Config error: missing required field '{field}'"

        friendly_msg = _ERROR_TYPE_MESSAGES.get(error_type, msg)
        suffix = f" ({len(errors) - 1} more)" if len(errors) > 1 else ""
        return f"Config error: field '{field}' - {friendly_msg}{suffix}"

    @staticmethod
    def _format_verbose_errors(errors: list[ErrorDetails]) -> str:
        lines: list[str] = [
            f"{Color.BOLD}{Color.RED}❌ Configuration Validation Error{Color.RESET}",
            "",
        ]

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
    def _format_single_error(idx: int, error_detail: ErrorDetails) -> list[str]:
        loc = error_detail.get("loc", ("unknown",))
        field = ".".join(str(p) for p in loc) if loc else "unknown"
        error_type = error_detail.get("type", "unknown_error")
        msg = error_detail.get("msg", "validation failed")
        input_value = error_detail.get("input", None)
        ctx = error_detail.get("ctx", {})

        lines: list[str] = [
            f"  {Color.BRIGHT_MAGENTA}[{idx}] Field: {Color.BOLD}{field}{Color.RESET}",
            f"      {Color.YELLOW}Error: {msg}{Color.RESET}",
            f"      {Color.DIM}Type: {error_type}{Color.RESET}",
        ]

        if input_value is not None:
            input_repr = repr(input_value)
            if len(input_repr) > 50:
                input_repr = input_repr[:47] + "..."
            lines.append(f"      {Color.DIM}Got: {input_repr}{Color.RESET}")

        if ctx:
            ctx_info = ErrorFormatter._format_context(ctx)
            if ctx_info:
                lines.append(f"      {Color.DIM}{ctx_info}{Color.RESET}")

        lines.append("")
        return lines

    @staticmethod
    def _format_context(ctx: dict[str, Any]) -> str:
        parts: list[str] = []
        if "min_length" in ctx:
            parts.append(f"min_length={ctx['min_length']}")
        if "max_length" in ctx:
            parts.append(f"max_length={ctx['max_length']}")
        if "gt" in ctx:
            parts.append(f"must be > {ctx['gt']}")
        if "ge" in ctx:
            parts.append(f"must be >= {ctx['ge']}")
        if "lt" in ctx:
            parts.append(f"must be < {ctx['lt']}")
        if "le" in ctx:
            parts.append(f"must be <= {ctx['le']}")
        if "expected" in ctx:
            parts.append(f"expected: {ctx['expected']}")
        return ", ".join(parts)

    @staticmethod
    def _format_string_error(error_str: str, style: Literal["compact", "verbose"]) -> str:
        if style == "compact":
            if "field required" in error_str.lower():
                match = re.search(r"(\w+)\s*\n\s*Field required", error_str)
                if match:
                    return f"Config error: missing required field '{match.group(1)}'"
            return "Config error: validation failed"

        lines: list[str] = [
            f"{Color.BOLD}{Color.RED}❌ Configuration Validation Error{Color.RESET}",
            "",
        ]

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
    def _get_fix_suggestions() -> list[str]:
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
        input_value: Any | None = None,
        context: dict[str, Any] | None = None,
    ):
        self.field = field
        self.error_type = error_type
        self.message = message
        self.input_value = input_value
        self.context = context or {}

    def to_dict(self) -> dict[str, Any]:
        return {
            "field": self.field,
            "error_type": self.error_type,
            "message": self.message,
            "input_value": self.input_value,
            "context": self.context,
        }

    def __repr__(self) -> str:
        return f"FieldErrorDetail(field={self.field!r}, error_type={self.error_type!r})"
