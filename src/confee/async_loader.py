"""Asynchronous configuration loading utilities."""

from __future__ import annotations

import asyncio
import contextlib
import logging
from collections.abc import Awaitable, Callable
from pathlib import Path
from typing import Any

logger = logging.getLogger(__name__)

# Type alias for watch callback
AsyncWatchCallback = Callable[[dict[str, Any], dict[str, Any]], Awaitable[None]]


class AsyncConfigLoader:
    """Asynchronous configuration file loader."""

    @staticmethod
    async def load(
        file_path: str | Path,
        strict: bool = True,
    ) -> dict[str, Any]:
        """Load configuration file asynchronously."""
        from .loaders import ConfigLoader

        loop = asyncio.get_running_loop()
        return await loop.run_in_executor(None, lambda: ConfigLoader.load(file_path, strict=strict))

    @staticmethod
    async def load_multiple(
        file_paths: list[str | Path],
        strict: bool = True,
    ) -> list[dict[str, Any]]:
        """Load multiple configuration files in parallel."""
        tasks = [AsyncConfigLoader.load(path, strict=strict) for path in file_paths]
        return await asyncio.gather(*tasks)

    @staticmethod
    async def load_remote(
        url: str,
        timeout: float = 30.0,
        headers: dict[str, str] | None = None,
    ) -> dict[str, Any]:
        """Load configuration from a remote URL.

        Raises:
            ImportError: If aiohttp is not installed
        """
        try:
            import aiohttp
        except ImportError:
            raise ImportError(
                "aiohttp is required for remote config loading. "
                "Install it with: pip install confee[remote]"
            ) from None

        import json

        import yaml

        async with aiohttp.ClientSession() as session:
            async with session.get(
                url, timeout=aiohttp.ClientTimeout(total=timeout), headers=headers
            ) as response:
                response.raise_for_status()
                content = await response.text()
                content_type = response.headers.get("Content-Type", "")

                if "json" in content_type or url.endswith(".json"):
                    return json.loads(content)
                if "yaml" in content_type or url.endswith((".yaml", ".yml")):
                    return yaml.safe_load(content)

                # Try YAML first (superset of JSON)
                try:
                    return yaml.safe_load(content)
                except yaml.YAMLError:
                    return json.loads(content)

    @staticmethod
    async def watch(
        file_path: str | Path,
        callback: AsyncWatchCallback,
        interval: float = 1.0,
    ) -> ConfigWatcher:
        """Watch a configuration file for changes."""
        watcher = ConfigWatcher(file_path, callback, interval)
        await watcher.start()
        return watcher


class ConfigWatcher:
    """Watch a configuration file for changes."""

    def __init__(
        self,
        file_path: str | Path,
        callback: AsyncWatchCallback,
        interval: float = 1.0,
    ):
        self.file_path = Path(file_path)
        self.callback = callback
        self.interval = interval
        self._task: asyncio.Task[None] | None = None
        self._running = False
        self._last_mtime: float | None = None
        self._last_config: dict[str, Any] | None = None

    async def start(self) -> None:
        """Start watching for changes."""
        if self._running:
            return

        self._running = True

        if self.file_path.exists():
            self._last_mtime = self.file_path.stat().st_mtime
            self._last_config = await AsyncConfigLoader.load(self.file_path)

        self._task = asyncio.create_task(self._watch_loop())

    async def stop(self) -> None:
        """Stop watching for changes."""
        self._running = False
        if self._task:
            self._task.cancel()
            with contextlib.suppress(asyncio.CancelledError):
                await self._task
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
                    except Exception:
                        logger.debug("Config reload error", exc_info=True)

            except asyncio.CancelledError:
                break


class ConfigMerger:
    """Utilities for merging multiple configurations."""

    @staticmethod
    def deep_merge(
        base: dict[str, Any],
        override: dict[str, Any],
        merge_lists: bool = False,
    ) -> dict[str, Any]:
        """Deep merge two configuration dictionaries."""
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
        file_paths: list[str | Path],
        merge_lists: bool = False,
    ) -> dict[str, Any]:
        """Load and merge multiple configuration files."""
        configs = await AsyncConfigLoader.load_multiple(file_paths)

        if not configs:
            return {}

        result = configs[0]
        for config in configs[1:]:
            result = ConfigMerger.deep_merge(result, config, merge_lists)

        return result
