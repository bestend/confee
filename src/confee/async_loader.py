"""Asynchronous configuration loading utilities.

This module provides async versions of configuration loading functions
for use in async/await contexts and for loading remote configurations.
"""

import asyncio
from pathlib import Path
from typing import Any, Awaitable, Callable, Dict, List, Optional, Type, TypeVar, Union

from .config import ConfigBase

T = TypeVar("T", bound=ConfigBase)


class AsyncConfigLoader:
    """Asynchronous configuration file loader.

    Provides async methods for loading configuration files, useful for:
    - Non-blocking file I/O in async applications
    - Loading remote configurations (HTTP, S3)
    - Parallel loading of multiple config files

    Examples:
        >>> async def main():
        ...     config = await AsyncConfigLoader.load("config.yaml")
        ...     app_config = await AsyncConfigLoader.load_as(
        ...         "config.yaml", AppConfig
        ...     )
    """

    @staticmethod
    async def load(
        file_path: Union[str, Path],
        strict: bool = True,
    ) -> Dict[str, Any]:
        """Load configuration file asynchronously.

        Args:
            file_path: Path to configuration file
            strict: If True, raise error on invalid format

        Returns:
            Configuration dictionary

        Examples:
            >>> config = await AsyncConfigLoader.load("config.yaml")
        """
        from .loaders import ConfigLoader

        # Run file I/O in thread pool to avoid blocking
        loop = asyncio.get_running_loop()
        return await loop.run_in_executor(None, lambda: ConfigLoader.load(file_path, strict=strict))

    @staticmethod
    async def load_as(
        file_path: Union[str, Path],
        config_class: Type[T],
        strict: bool = True,
    ) -> T:
        """Load configuration into a specific class asynchronously.

        Args:
            file_path: Path to configuration file
            config_class: Configuration class to instantiate
            strict: If True, raise error on validation failure

        Returns:
            Configuration instance

        Examples:
            >>> config = await AsyncConfigLoader.load_as("config.yaml", AppConfig)
        """
        data = await AsyncConfigLoader.load(file_path, strict=strict)
        return config_class(**data)

    @staticmethod
    async def load_multiple(
        file_paths: List[Union[str, Path]],
        strict: bool = True,
    ) -> List[Dict[str, Any]]:
        """Load multiple configuration files in parallel.

        Args:
            file_paths: List of configuration file paths
            strict: If True, raise error on invalid format

        Returns:
            List of configuration dictionaries

        Examples:
            >>> configs = await AsyncConfigLoader.load_multiple([
            ...     "base.yaml",
            ...     "production.yaml",
            ...     "secrets.yaml",
            ... ])
        """
        tasks = [AsyncConfigLoader.load(path, strict=strict) for path in file_paths]
        return await asyncio.gather(*tasks)

    @staticmethod
    async def load_remote(
        url: str,
        timeout: float = 30.0,
        headers: Optional[Dict[str, str]] = None,
    ) -> Dict[str, Any]:
        """Load configuration from a remote URL.

        Supports HTTP/HTTPS URLs. Automatically detects format from
        Content-Type header or URL extension.

        Args:
            url: Remote configuration URL
            timeout: Request timeout in seconds
            headers: Optional HTTP headers

        Returns:
            Configuration dictionary

        Raises:
            ImportError: If aiohttp is not installed
            ValueError: If content type is not supported

        Examples:
            >>> config = await AsyncConfigLoader.load_remote(
            ...     "https://config.example.com/app.yaml"
            ... )
        """
        try:
            import aiohttp
        except ImportError:
            raise ImportError(
                "aiohttp is required for remote config loading. "
                "Install it with: pip install confee[remote]"
            )

        import json

        import yaml

        async with aiohttp.ClientSession() as session:
            async with session.get(
                url, timeout=aiohttp.ClientTimeout(total=timeout), headers=headers
            ) as response:
                response.raise_for_status()
                content = await response.text()
                content_type = response.headers.get("Content-Type", "")

                # Detect format from content type or URL
                if "json" in content_type or url.endswith(".json"):
                    return json.loads(content)
                elif "yaml" in content_type or url.endswith((".yaml", ".yml")):
                    return yaml.safe_load(content)
                else:
                    # Try YAML first (superset of JSON)
                    try:
                        return yaml.safe_load(content)
                    except Exception:
                        return json.loads(content)

    @staticmethod
    async def watch(
        file_path: Union[str, Path],
        callback: "AsyncWatchCallback",
        interval: float = 1.0,
    ) -> "ConfigWatcher":
        """Watch a configuration file for changes.

        Args:
            file_path: Path to configuration file
            callback: Async callback function called on changes
            interval: Check interval in seconds

        Returns:
            ConfigWatcher instance (call .stop() to stop watching)

        Examples:
            >>> async def on_change(old, new):
            ...     print(f"Config changed: {old} -> {new}")
            ...
            >>> watcher = await AsyncConfigLoader.watch("config.yaml", on_change)
            >>> # Later...
            >>> await watcher.stop()
        """
        watcher = ConfigWatcher(file_path, callback, interval)
        await watcher.start()
        return watcher


# Type alias for watch callback
AsyncWatchCallback = Callable[[Dict[str, Any], Dict[str, Any]], Awaitable[None]]


class ConfigWatcher:
    """Watch a configuration file for changes.

    Examples:
        >>> watcher = ConfigWatcher("config.yaml", on_change_callback)
        >>> await watcher.start()
        >>> # ... application runs ...
        >>> await watcher.stop()
    """

    def __init__(
        self,
        file_path: Union[str, Path],
        callback: Any,  # AsyncWatchCallback
        interval: float = 1.0,
    ):
        """Initialize watcher.

        Args:
            file_path: Path to watch
            callback: Async callback on changes
            interval: Check interval in seconds
        """
        self.file_path = Path(file_path)
        self.callback = callback
        self.interval = interval
        self._task: Optional[asyncio.Task] = None
        self._running = False
        self._last_mtime: Optional[float] = None
        self._last_config: Optional[Dict[str, Any]] = None

    async def start(self) -> None:
        """Start watching for changes."""
        if self._running:
            return

        self._running = True

        # Get initial state
        if self.file_path.exists():
            self._last_mtime = self.file_path.stat().st_mtime
            self._last_config = await AsyncConfigLoader.load(self.file_path)

        self._task = asyncio.create_task(self._watch_loop())

    async def stop(self) -> None:
        """Stop watching for changes."""
        self._running = False
        if self._task:
            self._task.cancel()
            try:
                await self._task
            except asyncio.CancelledError:
                # Task cancellation during shutdown is expected and can be safely ignored.
                pass
            self._task = None

    async def _watch_loop(self) -> None:
        """Internal watch loop."""
        while self._running:
            try:
                await asyncio.sleep(self.interval)

                if not self.file_path.exists():
                    continue

                current_mtime = self.file_path.stat().st_mtime

                if self._last_mtime is None or current_mtime > self._last_mtime:
                    self._last_mtime = current_mtime

                    try:
                        new_config = await AsyncConfigLoader.load(self.file_path)

                        if self._last_config != new_config:
                            old_config = self._last_config
                            self._last_config = new_config
                            await self.callback(old_config or {}, new_config)
                    except Exception as e:
                        # Log or handle reload errors; config watch continues with previous config.
                        # Errors during reload are non-fatal to keep the watcher running.
                        import logging

                        logging.getLogger(__name__).debug(f"Config reload error: {e}")

            except asyncio.CancelledError:
                break


class ConfigMerger:
    """Utilities for merging multiple configurations.

    Examples:
        >>> base = {"debug": False, "workers": 4}
        >>> override = {"debug": True}
        >>> merged = ConfigMerger.deep_merge(base, override)
        >>> merged
        {'debug': True, 'workers': 4}
    """

    @staticmethod
    def deep_merge(
        base: Dict[str, Any],
        override: Dict[str, Any],
        merge_lists: bool = False,
    ) -> Dict[str, Any]:
        """Deep merge two configuration dictionaries.

        Args:
            base: Base configuration
            override: Override configuration (takes precedence)
            merge_lists: If True, concatenate lists; if False, replace

        Returns:
            Merged configuration dictionary

        Examples:
            >>> base = {"db": {"host": "localhost", "port": 5432}}
            >>> override = {"db": {"host": "production-db"}}
            >>> ConfigMerger.deep_merge(base, override)
            {'db': {'host': 'production-db', 'port': 5432}}
        """
        result = base.copy()

        for key, value in override.items():
            if key in result:
                if isinstance(result[key], dict) and isinstance(value, dict):
                    result[key] = ConfigMerger.deep_merge(result[key], value, merge_lists)
                elif merge_lists and isinstance(result[key], list) and isinstance(value, list):
                    result[key] = result[key] + value
                else:
                    result[key] = value
            else:
                result[key] = value

        return result

    @staticmethod
    async def merge_files(
        file_paths: List[Union[str, Path]],
        merge_lists: bool = False,
    ) -> Dict[str, Any]:
        """Load and merge multiple configuration files.

        Files are merged in order, with later files taking precedence.

        Args:
            file_paths: List of configuration file paths
            merge_lists: If True, concatenate lists; if False, replace

        Returns:
            Merged configuration dictionary

        Examples:
            >>> config = await ConfigMerger.merge_files([
            ...     "base.yaml",
            ...     "production.yaml",
            ... ])
        """
        configs = await AsyncConfigLoader.load_multiple(file_paths)

        if not configs:
            return {}

        result = configs[0]
        for config in configs[1:]:
            result = ConfigMerger.deep_merge(result, config, merge_lists)

        return result
