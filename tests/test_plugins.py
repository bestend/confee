"""Tests for plugins module."""

from __future__ import annotations

from pathlib import Path
from typing import Any

import pytest

from confee.plugins import (
    LoaderPlugin,
    PluginRegistry,
    SourcePlugin,
)


@pytest.fixture(autouse=True)
def clear_registry() -> None:
    """Clear plugin registry before each test."""
    PluginRegistry.clear()


class TestLoaderPlugin:
    def test_can_handle_matching_extension(self) -> None:
        class TestLoader(LoaderPlugin):
            extensions = [".test", ".tst"]

            def load(self, file_path: Path) -> dict[str, Any]:
                return {}

        loader = TestLoader()
        assert loader.can_handle(Path("config.test")) is True
        assert loader.can_handle(Path("config.tst")) is True
        assert loader.can_handle(Path("config.yaml")) is False

    def test_can_handle_case_insensitive(self) -> None:
        class TestLoader(LoaderPlugin):
            extensions = [".test"]

            def load(self, file_path: Path) -> dict[str, Any]:
                return {}

        loader = TestLoader()
        assert loader.can_handle(Path("config.TEST")) is True


class TestSourcePlugin:
    def test_can_handle_matching_scheme(self) -> None:
        class TestSource(SourcePlugin):
            scheme = "test"

            def load(self, uri: str) -> dict[str, Any]:
                return {}

        source = TestSource()
        assert source.can_handle("test://example.com/config") is True
        assert source.can_handle("http://example.com/config") is False


class TestPluginRegistry:
    def test_register_loader(self) -> None:
        class CustomLoader(LoaderPlugin):
            extensions = [".custom"]

            def load(self, file_path: Path) -> dict[str, Any]:
                return {"loaded": True}

        loader = CustomLoader()
        PluginRegistry.register_loader(loader)

        result = PluginRegistry.get_loader(Path("config.custom"))
        assert result is loader

    def test_register_loader_function(self) -> None:
        def custom_loader(file_path: str | Path) -> dict[str, Any]:
            return {"loaded": True}

        PluginRegistry.register_loader_function(".custom", custom_loader)

        result = PluginRegistry.get_loader(Path("config.custom"))
        assert result is custom_loader

    def test_loader_decorator(self) -> None:
        @PluginRegistry.loader(".decorated")
        def decorated_loader(file_path: str | Path) -> dict[str, Any]:
            return {"decorated": True}

        result = PluginRegistry.get_loader(Path("config.decorated"))
        assert result is decorated_loader

    def test_loader_decorator_multiple_extensions(self) -> None:
        @PluginRegistry.loader(".ext1", ".ext2")
        def multi_loader(file_path: str | Path) -> dict[str, Any]:
            return {"multi": True}

        assert PluginRegistry.get_loader(Path("file.ext1")) is multi_loader
        assert PluginRegistry.get_loader(Path("file.ext2")) is multi_loader

    def test_get_loader_not_found(self) -> None:
        result = PluginRegistry.get_loader(Path("config.unknown"))
        assert result is None

    def test_register_source(self) -> None:
        class CustomSource(SourcePlugin):
            scheme = "custom"

            def load(self, uri: str) -> dict[str, Any]:
                return {"source": True}

        source = CustomSource()
        PluginRegistry.register_source(source)

        result = PluginRegistry.get_source("custom://example.com/config")
        assert result is source

    def test_get_source_not_found(self) -> None:
        result = PluginRegistry.get_source("unknown://example.com/config")
        assert result is None

    def test_register_validator(self) -> None:
        def my_validator(config: dict[str, Any]) -> dict[str, Any]:
            config["validated"] = True
            return config

        PluginRegistry.register_validator(my_validator)

        result = PluginRegistry.run_validators({"name": "test"})
        assert result["validated"] is True

    def test_validator_decorator(self) -> None:
        @PluginRegistry.validator()
        def decorated_validator(config: dict[str, Any]) -> dict[str, Any]:
            config["decorated_validation"] = True
            return config

        result = PluginRegistry.run_validators({})
        assert result["decorated_validation"] is True

    def test_register_pre_hook(self) -> None:
        def pre_hook(config: dict[str, Any]) -> dict[str, Any]:
            config["pre_hooked"] = True
            return config

        PluginRegistry.register_hook(pre_hook, stage="pre")

        result = PluginRegistry.run_pre_hooks({})
        assert result["pre_hooked"] is True

    def test_register_post_hook(self) -> None:
        def post_hook(config: dict[str, Any]) -> dict[str, Any]:
            config["post_hooked"] = True
            return config

        PluginRegistry.register_hook(post_hook, stage="post")

        result = PluginRegistry.run_post_hooks({})
        assert result["post_hooked"] is True

    def test_pre_load_decorator(self) -> None:
        @PluginRegistry.pre_load()
        def pre_load_hook(config: dict[str, Any]) -> dict[str, Any]:
            config["pre_loaded"] = True
            return config

        result = PluginRegistry.run_pre_hooks({})
        assert result["pre_loaded"] is True

    def test_post_load_decorator(self) -> None:
        @PluginRegistry.post_load()
        def post_load_hook(config: dict[str, Any]) -> dict[str, Any]:
            config["post_loaded"] = True
            return config

        result = PluginRegistry.run_post_hooks({})
        assert result["post_loaded"] is True

    def test_multiple_validators_run_in_order(self) -> None:
        order: list[int] = []

        @PluginRegistry.validator()
        def validator1(config: dict[str, Any]) -> dict[str, Any]:
            order.append(1)
            return config

        @PluginRegistry.validator()
        def validator2(config: dict[str, Any]) -> dict[str, Any]:
            order.append(2)
            return config

        PluginRegistry.run_validators({})
        assert order == [1, 2]

    def test_clear_removes_all_plugins(self) -> None:
        @PluginRegistry.loader(".test")
        def test_loader(file_path: str | Path) -> dict[str, Any]:
            return {}

        @PluginRegistry.validator()
        def test_validator(config: dict[str, Any]) -> dict[str, Any]:
            return config

        PluginRegistry.clear()

        assert PluginRegistry.get_loader(Path("file.test")) is None
        assert PluginRegistry.list_extensions() == []

    def test_list_extensions(self) -> None:
        @PluginRegistry.loader(".ext1")
        def loader1(file_path: str | Path) -> dict[str, Any]:
            return {}

        @PluginRegistry.loader(".ext2")
        def loader2(file_path: str | Path) -> dict[str, Any]:
            return {}

        extensions = PluginRegistry.list_extensions()
        assert ".ext1" in extensions
        assert ".ext2" in extensions

    def test_list_schemes(self) -> None:
        class Source1(SourcePlugin):
            scheme = "s1"

            def load(self, uri: str) -> dict[str, Any]:
                return {}

        class Source2(SourcePlugin):
            scheme = "s2"

            def load(self, uri: str) -> dict[str, Any]:
                return {}

        PluginRegistry.register_source(Source1())
        PluginRegistry.register_source(Source2())

        schemes = PluginRegistry.list_schemes()
        assert "s1" in schemes
        assert "s2" in schemes


class TestBuiltinPlugins:
    def test_toml_loader_registered(self) -> None:
        from confee.plugins import register_builtin_plugins

        PluginRegistry.clear()
        register_builtin_plugins()

        loader = PluginRegistry.get_loader(Path("config.toml"))
        assert loader is not None

    def test_toml_loader_works(self, tmp_path: Path) -> None:
        from confee.plugins import register_builtin_plugins

        PluginRegistry.clear()
        register_builtin_plugins()

        config_file = tmp_path / "config.toml"
        config_file.write_text('[section]\nkey = "value"')

        loader = PluginRegistry.get_loader(config_file)
        assert loader is not None

        result = loader(config_file)
        assert result == {"section": {"key": "value"}}


class TestLazyInitialization:
    def test_ensure_initialized_creates_empty_collections(self) -> None:
        PluginRegistry._loaders = None
        PluginRegistry._loader_functions = None
        PluginRegistry._sources = None
        PluginRegistry._validators = None
        PluginRegistry._pre_load_hooks = None
        PluginRegistry._post_load_hooks = None

        PluginRegistry._ensure_initialized()

        assert PluginRegistry._loaders == {}
        assert PluginRegistry._loader_functions == {}
        assert PluginRegistry._sources == {}
        assert PluginRegistry._validators == []
        assert PluginRegistry._pre_load_hooks == []
        assert PluginRegistry._post_load_hooks == []
