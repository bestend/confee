"""Plugin system for extending confee functionality.

This module provides a registry-based plugin architecture for:
- Custom format loaders (TOML, INI, etc.)
- Custom source handlers (HTTP, S3, etc.)
- Custom validators
- Pre/post load hooks
"""

from abc import ABC, abstractmethod
from pathlib import Path
from typing import Any, Callable, Dict, List, Optional, Type, Union

# Type aliases
LoaderFunction = Callable[[Union[str, Path]], Dict[str, Any]]
ValidatorFunction = Callable[[Dict[str, Any]], Dict[str, Any]]
HookFunction = Callable[[Dict[str, Any]], Dict[str, Any]]


class LoaderPlugin(ABC):
    """Abstract base class for format loader plugins.

    Implement this to add support for new configuration file formats.

    Examples:
        >>> class TomlLoader(LoaderPlugin):
        ...     extensions = [".toml"]
        ...
        ...     def load(self, file_path: Path) -> Dict[str, Any]:
        ...         import tomllib
        ...         with open(file_path, "rb") as f:
        ...             return tomllib.load(f)
        ...
        >>> PluginRegistry.register_loader(TomlLoader())
    """

    extensions: List[str] = []  # File extensions this loader handles

    @abstractmethod
    def load(self, file_path: Path) -> Dict[str, Any]:
        """Load configuration from file.

        Args:
            file_path: Path to configuration file

        Returns:
            Configuration dictionary
        """
        pass

    def can_handle(self, file_path: Path) -> bool:
        """Check if this loader can handle the given file.

        Args:
            file_path: Path to check

        Returns:
            True if this loader can handle the file
        """
        return file_path.suffix.lower() in self.extensions


class SourcePlugin(ABC):
    """Abstract base class for configuration source plugins.

    Implement this to add support for new configuration sources (HTTP, S3, etc.).

    Examples:
        >>> class HttpSource(SourcePlugin):
        ...     scheme = "http"
        ...
        ...     def load(self, uri: str) -> Dict[str, Any]:
        ...         import requests
        ...         response = requests.get(uri)
        ...         return response.json()
        ...
        >>> PluginRegistry.register_source(HttpSource())
    """

    scheme: str = ""  # URI scheme this source handles (http, s3, etc.)

    @abstractmethod
    def load(self, uri: str) -> Dict[str, Any]:
        """Load configuration from source.

        Args:
            uri: Source URI

        Returns:
            Configuration dictionary
        """
        pass

    def can_handle(self, uri: str) -> bool:
        """Check if this source can handle the given URI.

        Args:
            uri: URI to check

        Returns:
            True if this source can handle the URI
        """
        return uri.startswith(f"{self.scheme}://")


class PluginRegistry:
    """Central registry for confee plugins.

    Manages registration and discovery of:
    - Format loaders
    - Source handlers
    - Validators
    - Hooks

    Examples:
        >>> # Register a loader
        >>> PluginRegistry.register_loader(TomlLoader())
        >>>
        >>> # Register using decorator
        >>> @PluginRegistry.loader(".ini")
        ... def load_ini(file_path: Path) -> Dict[str, Any]:
        ...     import configparser
        ...     config = configparser.ConfigParser()
        ...     config.read(file_path)
        ...     return dict(config)
    """

    _loaders: Dict[str, LoaderPlugin] = {}
    _loader_functions: Dict[str, LoaderFunction] = {}
    _sources: Dict[str, SourcePlugin] = {}
    _validators: List[ValidatorFunction] = []
    _pre_load_hooks: List[HookFunction] = []
    _post_load_hooks: List[HookFunction] = []

    @classmethod
    def register_loader(cls, loader: LoaderPlugin) -> None:
        """Register a format loader plugin.

        Args:
            loader: Loader plugin instance
        """
        for ext in loader.extensions:
            cls._loaders[ext.lower()] = loader

    @classmethod
    def register_loader_function(cls, extension: str, func: LoaderFunction) -> None:
        """Register a loader function for a file extension.

        Args:
            extension: File extension (e.g., ".toml")
            func: Loader function
        """
        cls._loader_functions[extension.lower()] = func

    @classmethod
    def loader(cls, *extensions: str) -> Callable[[LoaderFunction], LoaderFunction]:
        """Decorator to register a loader function.

        Args:
            *extensions: File extensions to handle

        Returns:
            Decorator function

        Examples:
            >>> @PluginRegistry.loader(".toml")
            ... def load_toml(file_path: Path) -> Dict[str, Any]:
            ...     import tomllib
            ...     with open(file_path, "rb") as f:
            ...         return tomllib.load(f)
        """

        def decorator(func: LoaderFunction) -> LoaderFunction:
            for ext in extensions:
                cls.register_loader_function(ext, func)
            return func

        return decorator

    @classmethod
    def register_source(cls, source: SourcePlugin) -> None:
        """Register a source plugin.

        Args:
            source: Source plugin instance
        """
        cls._sources[source.scheme.lower()] = source

    @classmethod
    def register_validator(cls, validator: ValidatorFunction) -> None:
        """Register a validator function.

        Validators are called after loading and before creating the config object.

        Args:
            validator: Validator function that takes and returns a config dict
        """
        cls._validators.append(validator)

    @classmethod
    def validator(cls) -> Callable[[ValidatorFunction], ValidatorFunction]:
        """Decorator to register a validator function.

        Examples:
            >>> @PluginRegistry.validator()
            ... def require_debug_false_in_prod(config: Dict[str, Any]) -> Dict[str, Any]:
            ...     if config.get("env") == "prod" and config.get("debug"):
            ...         raise ValueError("Debug must be False in production")
            ...     return config
        """

        def decorator(func: ValidatorFunction) -> ValidatorFunction:
            cls.register_validator(func)
            return func

        return decorator

    @classmethod
    def register_hook(cls, hook: HookFunction, stage: str = "post") -> None:
        """Register a load hook.

        Args:
            hook: Hook function
            stage: "pre" (before loading) or "post" (after loading)
        """
        if stage == "pre":
            cls._pre_load_hooks.append(hook)
        else:
            cls._post_load_hooks.append(hook)

    @classmethod
    def pre_load(cls) -> Callable[[HookFunction], HookFunction]:
        """Decorator to register a pre-load hook.

        Examples:
            >>> @PluginRegistry.pre_load()
            ... def add_defaults(config: Dict[str, Any]) -> Dict[str, Any]:
            ...     config.setdefault("log_level", "INFO")
            ...     return config
        """

        def decorator(func: HookFunction) -> HookFunction:
            cls.register_hook(func, "pre")
            return func

        return decorator

    @classmethod
    def post_load(cls) -> Callable[[HookFunction], HookFunction]:
        """Decorator to register a post-load hook.

        Examples:
            >>> @PluginRegistry.post_load()
            ... def expand_paths(config: Dict[str, Any]) -> Dict[str, Any]:
            ...     if "data_dir" in config:
            ...         config["data_dir"] = os.path.expanduser(config["data_dir"])
            ...     return config
        """

        def decorator(func: HookFunction) -> HookFunction:
            cls.register_hook(func, "post")
            return func

        return decorator

    @classmethod
    def get_loader(cls, file_path: Path) -> Optional[Union[LoaderPlugin, LoaderFunction]]:
        """Get a loader for the given file path.

        Args:
            file_path: Path to configuration file

        Returns:
            Loader plugin or function, or None if not found
        """
        ext = file_path.suffix.lower()

        # Check plugin loaders first
        if ext in cls._loaders:
            return cls._loaders[ext]

        # Check function loaders
        if ext in cls._loader_functions:
            return cls._loader_functions[ext]

        return None

    @classmethod
    def get_source(cls, uri: str) -> Optional[SourcePlugin]:
        """Get a source handler for the given URI.

        Args:
            uri: Source URI

        Returns:
            Source plugin, or None if not found
        """
        for scheme, source in cls._sources.items():
            if uri.startswith(f"{scheme}://"):
                return source
        return None

    @classmethod
    def run_validators(cls, config: Dict[str, Any]) -> Dict[str, Any]:
        """Run all registered validators.

        Args:
            config: Configuration dictionary

        Returns:
            Validated configuration dictionary

        Raises:
            ValidationError: If validation fails
        """
        for validator in cls._validators:
            config = validator(config)
        return config

    @classmethod
    def run_pre_hooks(cls, config: Dict[str, Any]) -> Dict[str, Any]:
        """Run all pre-load hooks.

        Args:
            config: Configuration dictionary

        Returns:
            Modified configuration dictionary
        """
        for hook in cls._pre_load_hooks:
            config = hook(config)
        return config

    @classmethod
    def run_post_hooks(cls, config: Dict[str, Any]) -> Dict[str, Any]:
        """Run all post-load hooks.

        Args:
            config: Configuration dictionary

        Returns:
            Modified configuration dictionary
        """
        for hook in cls._post_load_hooks:
            config = hook(config)
        return config

    @classmethod
    def clear(cls) -> None:
        """Clear all registered plugins (useful for testing)."""
        cls._loaders.clear()
        cls._loader_functions.clear()
        cls._sources.clear()
        cls._validators.clear()
        cls._pre_load_hooks.clear()
        cls._post_load_hooks.clear()

    @classmethod
    def list_extensions(cls) -> List[str]:
        """List all registered file extensions.

        Returns:
            List of supported file extensions
        """
        extensions = set(cls._loaders.keys())
        extensions.update(cls._loader_functions.keys())
        return sorted(extensions)

    @classmethod
    def list_schemes(cls) -> List[str]:
        """List all registered URI schemes.

        Returns:
            List of supported URI schemes
        """
        return sorted(cls._sources.keys())


def register_builtin_plugins() -> None:
    """Register built-in loader plugins.

    This is called automatically when the module is imported.
    """
    # TOML support (Python 3.11+ or tomli)
    try:
        import sys

        if sys.version_info >= (3, 11):
            import tomllib

            @PluginRegistry.loader(".toml")
            def _load_toml(file_path: Path) -> Dict[str, Any]:
                with open(file_path, "rb") as f:
                    return tomllib.load(f)
        else:
            try:
                import tomli

                @PluginRegistry.loader(".toml")
                def _load_toml_backport(file_path: Path) -> Dict[str, Any]:
                    with open(file_path, "rb") as f:
                        return tomli.load(f)

            except ImportError:
                pass  # TOML not available
    except Exception as e:
        # Log TOML plugin registration errors instead of silently suppressing.
        import logging

        logging.getLogger(__name__).debug(f"TOML plugin registration skipped: {e}")


# Auto-register built-in plugins
register_builtin_plugins()
