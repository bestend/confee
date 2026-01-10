"""Tests for async_loader module."""

from __future__ import annotations

import asyncio
from pathlib import Path
from typing import Any

import pytest


class TestAsyncConfigLoader:
    @pytest.mark.asyncio
    async def test_load_yaml_file(self, tmp_path: Path) -> None:
        from confee.async_loader import AsyncConfigLoader

        config_file = tmp_path / "config.yaml"
        config_file.write_text("name: test\nvalue: 42")

        result = await AsyncConfigLoader.load(config_file)

        assert result == {"name": "test", "value": 42}

    @pytest.mark.asyncio
    async def test_load_json_file(self, tmp_path: Path) -> None:
        from confee.async_loader import AsyncConfigLoader

        config_file = tmp_path / "config.json"
        config_file.write_text('{"name": "test", "value": 42}')

        result = await AsyncConfigLoader.load(config_file)

        assert result == {"name": "test", "value": 42}

    @pytest.mark.asyncio
    async def test_load_multiple_files(self, tmp_path: Path) -> None:
        from confee.async_loader import AsyncConfigLoader

        file1 = tmp_path / "config1.yaml"
        file1.write_text("name: first")

        file2 = tmp_path / "config2.yaml"
        file2.write_text("name: second")

        results = await AsyncConfigLoader.load_multiple([file1, file2])

        assert len(results) == 2
        assert results[0] == {"name": "first"}
        assert results[1] == {"name": "second"}

    @pytest.mark.asyncio
    async def test_load_nonexistent_file_strict(self, tmp_path: Path) -> None:
        from confee.async_loader import AsyncConfigLoader

        with pytest.raises(FileNotFoundError):
            await AsyncConfigLoader.load(tmp_path / "nonexistent.yaml")

    @pytest.mark.asyncio
    async def test_load_nonexistent_file_lenient(self, tmp_path: Path) -> None:
        from confee.async_loader import AsyncConfigLoader

        result = await AsyncConfigLoader.load(tmp_path / "nonexistent.yaml", strict=False)
        assert result == {}


class TestConfigWatcher:
    @pytest.mark.asyncio
    async def test_watch_detects_changes(self, tmp_path: Path) -> None:
        from confee.async_loader import AsyncConfigLoader

        config_file = tmp_path / "config.yaml"
        config_file.write_text("name: initial")

        changes: list[tuple[dict, dict]] = []

        async def on_change(old: dict[str, Any], new: dict[str, Any]) -> None:
            changes.append((old, new))

        watcher = await AsyncConfigLoader.watch(config_file, on_change, interval=0.05)

        try:
            await asyncio.sleep(0.1)
            config_file.write_text("name: updated")
            await asyncio.sleep(0.2)
        finally:
            await watcher.stop()

        assert len(changes) >= 1
        assert changes[-1][1] == {"name": "updated"}

    @pytest.mark.asyncio
    async def test_watch_stop_cancels_task(self, tmp_path: Path) -> None:
        from confee.async_loader import AsyncConfigLoader

        config_file = tmp_path / "config.yaml"
        config_file.write_text("name: test")

        async def on_change(old: dict[str, Any], new: dict[str, Any]) -> None:
            pass

        watcher = await AsyncConfigLoader.watch(config_file, on_change, interval=0.05)

        assert watcher._running is True
        assert watcher._task is not None

        await watcher.stop()

        assert watcher._running is False
        assert watcher._task is None

    @pytest.mark.asyncio
    async def test_watch_start_idempotent(self, tmp_path: Path) -> None:
        from confee.async_loader import ConfigWatcher

        config_file = tmp_path / "config.yaml"
        config_file.write_text("name: test")

        async def on_change(old: dict[str, Any], new: dict[str, Any]) -> None:
            pass

        watcher = ConfigWatcher(config_file, on_change, interval=0.05)

        await watcher.start()
        first_task = watcher._task
        await watcher.start()

        assert watcher._task is first_task

        await watcher.stop()

    @pytest.mark.asyncio
    async def test_watch_handles_missing_file(self, tmp_path: Path) -> None:
        from confee.async_loader import ConfigWatcher

        config_file = tmp_path / "nonexistent.yaml"

        async def on_change(old: dict[str, Any], new: dict[str, Any]) -> None:
            pass

        watcher = ConfigWatcher(config_file, on_change, interval=0.05)
        await watcher.start()

        assert watcher._last_mtime is None
        assert watcher._last_config is None

        await watcher.stop()


class TestConfigMerger:
    def test_deep_merge_simple(self) -> None:
        from confee.async_loader import ConfigMerger

        base = {"a": 1, "b": 2}
        override = {"b": 3, "c": 4}

        result = ConfigMerger.deep_merge(base, override)

        assert result == {"a": 1, "b": 3, "c": 4}

    def test_deep_merge_nested(self) -> None:
        from confee.async_loader import ConfigMerger

        base = {"db": {"host": "localhost", "port": 5432}}
        override = {"db": {"host": "prod-db"}}

        result = ConfigMerger.deep_merge(base, override)

        assert result == {"db": {"host": "prod-db", "port": 5432}}

    def test_deep_merge_lists_replace(self) -> None:
        from confee.async_loader import ConfigMerger

        base = {"items": [1, 2, 3]}
        override = {"items": [4, 5]}

        result = ConfigMerger.deep_merge(base, override, merge_lists=False)

        assert result == {"items": [4, 5]}

    def test_deep_merge_lists_concatenate(self) -> None:
        from confee.async_loader import ConfigMerger

        base = {"items": [1, 2, 3]}
        override = {"items": [4, 5]}

        result = ConfigMerger.deep_merge(base, override, merge_lists=True)

        assert result == {"items": [1, 2, 3, 4, 5]}

    @pytest.mark.asyncio
    async def test_merge_files(self, tmp_path: Path) -> None:
        from confee.async_loader import ConfigMerger

        base = tmp_path / "base.yaml"
        base.write_text("name: base\nvalue: 1")

        override = tmp_path / "override.yaml"
        override.write_text("value: 2\nextra: true")

        result = await ConfigMerger.merge_files([base, override])

        assert result == {"name": "base", "value": 2, "extra": True}

    @pytest.mark.asyncio
    async def test_merge_files_empty(self) -> None:
        from confee.async_loader import ConfigMerger

        result = await ConfigMerger.merge_files([])

        assert result == {}

    @pytest.mark.asyncio
    async def test_merge_files_with_merge_lists(self, tmp_path: Path) -> None:
        from confee.async_loader import ConfigMerger

        file1 = tmp_path / "file1.yaml"
        file1.write_text("items:\n  - a\n  - b")

        file2 = tmp_path / "file2.yaml"
        file2.write_text("items:\n  - c")

        result = await ConfigMerger.merge_files([file1, file2], merge_lists=True)

        assert result == {"items": ["a", "b", "c"]}


class TestAsyncConfigLoaderRemote:
    @pytest.mark.asyncio
    async def test_load_remote_import_error(self) -> None:
        import sys

        from confee.async_loader import AsyncConfigLoader

        original = sys.modules.get("aiohttp")
        sys.modules["aiohttp"] = None  # type: ignore

        try:
            with pytest.raises(ImportError, match="aiohttp is required"):
                await AsyncConfigLoader.load_remote("https://example.com/config.yaml")
        finally:
            if original is not None:
                sys.modules["aiohttp"] = original
            else:
                sys.modules.pop("aiohttp", None)
