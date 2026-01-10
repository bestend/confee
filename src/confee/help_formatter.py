"""Help text generation for configuration classes."""

from __future__ import annotations

import sys
from typing import TYPE_CHECKING, Any

from .colors import Color

if TYPE_CHECKING:
    from .config import ConfigBase


class HelpFormatter:
    """Format and display help messages for configuration classes.

    Generates colorized, typer-style help output for Pydantic configuration classes.

    Examples:
        >>> class AppConfig(ConfigBase):
        ...     name: str
        ...     debug: bool = False
        >>> HelpFormatter.print_help(AppConfig)
    """

    @staticmethod
    def _is_config_base_subclass(field_type: Any) -> bool:
        import inspect
        from typing import get_args, get_origin

        from .config import ConfigBase

        if field_type is type(None):
            return False

        if inspect.isclass(field_type):
            try:
                return issubclass(field_type, ConfigBase)
            except TypeError:
                return False

        origin = get_origin(field_type)
        if origin is not None:
            args = get_args(field_type)
            for arg in args:
                if arg is type(None):
                    continue
                if inspect.isclass(arg):
                    try:
                        if issubclass(arg, ConfigBase):
                            return True
                    except TypeError:
                        continue

        return False

    @staticmethod
    def _get_config_base_type(field_type: Any) -> type[ConfigBase] | None:
        import inspect
        from typing import get_args, get_origin

        from .config import ConfigBase

        if inspect.isclass(field_type):
            try:
                if issubclass(field_type, ConfigBase):
                    return field_type
            except TypeError:
                pass

        origin = get_origin(field_type)
        if origin is not None:
            args = get_args(field_type)
            for arg in args:
                if arg is type(None):
                    continue
                if inspect.isclass(arg):
                    try:
                        if issubclass(arg, ConfigBase):
                            return arg
                    except TypeError:
                        continue

        return None

    @staticmethod
    def _format_type_annotation(field_type: Any) -> str:
        import types
        import typing

        if field_type is None:
            return "None"

        origin = typing.get_origin(field_type)
        args = typing.get_args(field_type)

        if origin is typing.Union or isinstance(field_type, types.UnionType):
            non_none_args = [a for a in args if a is not type(None)]
            if len(non_none_args) == 1 and type(None) in args:
                inner = HelpFormatter._format_type_annotation(non_none_args[0])
                return f"{inner}?"
            formatted = [HelpFormatter._format_type_annotation(a) for a in args]
            return " | ".join(formatted)

        if origin is typing.Literal:
            values = ", ".join(repr(a) for a in args)
            return f"Literal[{values}]"

        if origin is list:
            if args:
                inner = HelpFormatter._format_type_annotation(args[0])
                return f"list[{inner}]"
            return "list"

        if origin is dict:
            if len(args) >= 2:
                k = HelpFormatter._format_type_annotation(args[0])
                v = HelpFormatter._format_type_annotation(args[1])
                return f"dict[{k}, {v}]"
            return "dict"

        if origin is tuple:
            if args:
                inner = ", ".join(HelpFormatter._format_type_annotation(a) for a in args)
                return f"tuple[{inner}]"
            return "tuple"

        if origin is set:
            if args:
                inner = HelpFormatter._format_type_annotation(args[0])
                return f"set[{inner}]"
            return "set"

        if hasattr(field_type, "__name__"):
            return field_type.__name__

        return str(field_type).replace("typing.", "")

    @staticmethod
    def _format_default_field(field: Any) -> str:
        """Return a colored default-string segment for a Pydantic v2 field.

        Rules:
        - default_factory present: factory()
        - default is explicitly None: None
        - required (no default and no factory): <required>
        - otherwise: actual default value
        """
        # Detect Pydantic's undefined sentinel
        _PUD: Any
        try:
            from pydantic_core import PydanticUndefined

            _PUD = PydanticUndefined  # type: ignore[assignment]
        except Exception:
            try:
                from pydantic import PydanticUndefined  # type: ignore[no-redef]

                _PUD = PydanticUndefined  # type: ignore[assignment]
            except Exception:
                _PUD = object()  # type: ignore[assignment]

        # 1) Prioritize default_factory
        if getattr(field, "default_factory", None) is not None:
            factory = getattr(field.default_factory, "__name__", "factory")
            return f" {Color.BRIGHT_YELLOW}[default: {factory}()]{Color.RESET}"

        # 2) Explicit None
        if getattr(field, "default", None) is None and hasattr(field, "default"):
            return f" {Color.BRIGHT_YELLOW}[default: None]{Color.RESET}"

        # 3) Determine required
        is_required_method = getattr(field, "is_required", None)
        is_required = False
        if callable(is_required_method):
            try:
                is_required = bool(is_required_method())
            except Exception:
                is_required = False

        if is_required or getattr(field, "default", _PUD) is _PUD:
            return ""

        # 4) Render actual default value
        return f" {Color.BRIGHT_YELLOW}[default: {field.default}]{Color.RESET}"

    @staticmethod
    def _collect_fields_recursive(
        config_class: type[ConfigBase],
        prefix: str = "",
        max_depth: int = 5,
        visited: set | None = None,
    ) -> list[tuple[str, str, str, str]]:
        if visited is None:
            visited = set()

        if max_depth <= 0 or config_class in visited:
            return []

        visited = visited.copy()
        visited.add(config_class)

        field_info: list[tuple[str, str, str, str]] = []

        if not hasattr(config_class, "model_fields"):
            return field_info

        for field_name, field in config_class.model_fields.items():
            field_type = field.annotation
            full_name = f"{prefix}{field_name}" if prefix else field_name

            nested_config_class = HelpFormatter._get_config_base_type(field_type)

            if nested_config_class is not None:
                nested_fields = HelpFormatter._collect_fields_recursive(
                    nested_config_class,
                    prefix=f"{full_name}.",
                    max_depth=max_depth - 1,
                    visited=visited,
                )
                field_info.extend(nested_fields)
            else:
                type_str = HelpFormatter._format_type_annotation(field_type)

                description_text = field.description or field_name.replace("_", " ")
                if prefix:
                    prefix_clean = prefix.rstrip(".")
                    description_text = f"{prefix_clean} {description_text}"

                default_str = HelpFormatter._format_default_field(field)
                field_info.append((full_name, type_str, description_text, default_str))

        return field_info

    @staticmethod
    def generate_help(
        config_class: type[ConfigBase],
        program_name: str | None = None,
        description: str | None = None,
    ) -> str:
        """Generate help text for a configuration class with colors.

        Args:
            config_class: Configuration class to generate help for
            program_name: Name of the program (default: sys.argv[0])
            description: Custom description text

        Returns:
            Formatted help text with ANSI colors

        Examples:
            >>> help_text = HelpFormatter.generate_help(AppConfig)
            >>> print(help_text)
        """
        if program_name is None:
            program_name = sys.argv[0]

        help_text = (
            f"{Color.BOLD}{Color.BRIGHT_CYAN}Usage:{Color.RESET} {program_name} [OPTIONS]\n\n"
        )

        if description:
            help_text += f"{Color.BOLD}Description:{Color.RESET}\n  {description}\n\n"

        help_text += f"{Color.BOLD}{Color.BRIGHT_CYAN}Options:{Color.RESET}\n"

        field_info = HelpFormatter._collect_fields_recursive(config_class)

        if field_info:
            max_name_width = max(len(name) for name, _, _, _ in field_info)
            max_type_width = max(len(type_str) for _, type_str, _, _ in field_info)

            for name, type_str, desc, default in field_info:
                help_text += f"  {Color.BRIGHT_GREEN}--{name}{Color.RESET}"
                help_text += " " * (max_name_width - len(name) + 2)
                help_text += f"{Color.CYAN}{type_str:<{max_type_width}}{Color.RESET}  "
                help_text += f"{desc}{default}\n"

        help_text += f"\n{Color.BOLD}{Color.BRIGHT_CYAN}Override format:{Color.RESET}\n"
        help_text += f"  {Color.GREEN}key=value{Color.RESET}              Set a simple value\n"
        help_text += f"  {Color.GREEN}nested.key=value{Color.RESET}       Set a nested value\n"
        help_text += f"  {Color.GREEN}@file:path/to/file{Color.RESET}     Read value from file\n"
        help_text += f"  {Color.GREEN}true/false/yes/no/on/off{Color.RESET} for boolean values\n"
        help_text += f"\n{Color.BOLD}{Color.BRIGHT_CYAN}Examples:{Color.RESET}\n"
        help_text += f"  {Color.MAGENTA}{program_name} debug=true workers=8{Color.RESET}\n"
        help_text += f"  {Color.MAGENTA}{program_name} --help{Color.RESET}\n"

        return help_text

    @staticmethod
    def print_help(
        config_class: type[ConfigBase],
        program_name: str | None = None,
        description: str | None = None,
        exit_code: int = 0,
    ) -> None:
        help_text = HelpFormatter.generate_help(config_class, program_name, description)
        print(help_text)
        if exit_code is not None:
            sys.exit(exit_code)

    @staticmethod
    def generate_markdown_docs(
        config_class: type[ConfigBase],
        title: str | None = None,
    ) -> str:
        """Generate Markdown documentation for a configuration class.

        Args:
            config_class: Configuration class to document
            title: Optional title for the documentation

        Returns:
            Markdown-formatted documentation string

        Examples:
            >>> docs = HelpFormatter.generate_markdown_docs(AppConfig, "Application Config")
            >>> with open("CONFIG.md", "w") as f:
            ...     f.write(docs)
        """
        if title is None:
            title = config_class.__name__

        lines = [f"# {title}", ""]

        if config_class.__doc__:
            lines.append(config_class.__doc__.strip())
            lines.append("")

        lines.append("## Configuration Options")
        lines.append("")
        lines.append("| Option | Type | Description | Default |")
        lines.append("|--------|------|-------------|---------|")

        field_info = HelpFormatter._collect_fields_recursive(config_class)

        for name, type_str, desc, default_colored in field_info:
            # Strip ANSI codes from default
            import re

            default = re.sub(r"\033\[[0-9;]*m", "", default_colored)
            default = default.replace("[default: ", "").rstrip("]").strip()
            if not default:
                default = "*required*"

            lines.append(f"| `{name}` | `{type_str}` | {desc} | {default} |")

        lines.append("")
        lines.append("## Usage Examples")
        lines.append("")
        lines.append("```bash")
        lines.append("# Using CLI arguments")
        lines.append("python main.py debug=true workers=8")
        lines.append("")
        lines.append("# Using environment variables")
        lines.append("export CONFEE_DEBUG=true")
        lines.append("export CONFEE_WORKERS=8")
        lines.append("python main.py")
        lines.append("```")

        return "\n".join(lines)
