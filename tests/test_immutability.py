"""Tests for config freeze/unfreeze/immutability functionality.

This module tests the freeze/unfreeze feature which prevents accidental
modification of configuration objects at runtime.
"""

import pytest

from confee import ConfigBase


class SimpleConfig(ConfigBase):
    """Simple config for basic freeze tests."""

    name: str
    value: int


class NestedConfig(ConfigBase):
    """Config with nested structure for propagation tests."""

    app_name: str
    port: int


class ParentConfig(ConfigBase):
    """Parent config containing nested configs."""

    environment: str
    service: NestedConfig


class TestFreezeBasics:
    """Test basic freeze/unfreeze functionality."""

    def test_freeze_prevents_modification(self):
        """Test that freeze() prevents attribute modification."""
        config = SimpleConfig(name="test", value=42)
        config.freeze()

        with pytest.raises(AttributeError, match="Cannot modify frozen configuration"):
            config.name = "changed"

        with pytest.raises(AttributeError, match="Cannot modify frozen configuration"):
            config.value = 100

    def test_unfreeze_allows_modification(self):
        """Test that unfreeze() restores mutability."""
        config = SimpleConfig(name="test", value=42)
        config.freeze()

        # Should raise while frozen
        with pytest.raises(AttributeError):
            config.name = "changed"

        # Unfreeze and modify
        config.unfreeze()
        config.name = "changed"
        config.value = 100

        assert config.name == "changed"
        assert config.value == 100

    def test_freeze_returns_self(self):
        """Test that freeze() returns self for method chaining."""
        config = SimpleConfig(name="test", value=42)
        result = config.freeze()

        assert result is config
        assert config.is_frozen()

    def test_unfreeze_returns_self(self):
        """Test that unfreeze() returns self for method chaining."""
        config = SimpleConfig(name="test", value=42).freeze()
        result = config.unfreeze()

        assert result is config
        assert not config.is_frozen()

    def test_is_frozen_state(self):
        """Test is_frozen() correctly reports state."""
        config = SimpleConfig(name="test", value=42)

        assert not config.is_frozen()

        config.freeze()
        assert config.is_frozen()

        config.unfreeze()
        assert not config.is_frozen()

    def test_freeze_error_message(self):
        """Test that frozen modification error message is helpful."""
        config = SimpleConfig(name="test", value=42).freeze()

        with pytest.raises(AttributeError) as exc_info:
            config.name = "changed"

        error_msg = str(exc_info.value)
        assert "Cannot modify frozen configuration" in error_msg
        assert "unfreeze()" in error_msg

    def test_multiple_freeze_calls(self):
        """Test that multiple freeze() calls don't break anything."""
        config = SimpleConfig(name="test", value=42)
        config.freeze()
        config.freeze()  # Should be idempotent

        assert config.is_frozen()

        with pytest.raises(AttributeError):
            config.name = "changed"

    def test_multiple_unfreeze_calls(self):
        """Test that multiple unfreeze() calls don't break anything."""
        config = SimpleConfig(name="test", value=42).freeze()
        config.unfreeze()
        config.unfreeze()  # Should be idempotent

        assert not config.is_frozen()
        config.name = "changed"  # Should work
        assert config.name == "changed"


class TestCopyUnfrozen:
    """Test copy_unfrozen() functionality."""

    def test_copy_creates_mutable_instance(self):
        """Test that copy_unfrozen() creates a mutable copy."""
        original = SimpleConfig(name="test", value=42).freeze()
        copy = original.copy_unfrozen()

        # Original should still be frozen
        assert original.is_frozen()
        with pytest.raises(AttributeError):
            original.name = "changed"

        # Copy should be mutable
        assert not copy.is_frozen()
        copy.name = "changed"
        copy.value = 100

        assert copy.name == "changed"
        assert copy.value == 100

    def test_copy_has_same_values(self):
        """Test that copy_unfrozen() preserves all values."""
        original = SimpleConfig(name="original", value=999).freeze()
        copy = original.copy_unfrozen()

        assert copy.name == "original"
        assert copy.value == 999

    def test_copy_is_independent(self):
        """Test that modifications to copy don't affect original."""
        original = SimpleConfig(name="original", value=42)
        original.freeze()
        copy = original.copy_unfrozen()

        copy.name = "modified"
        copy.value = 100

        # Original should be unchanged (and still frozen)
        original.unfreeze()
        assert original.name == "original"
        assert original.value == 42

    def test_copy_of_unfrozen(self):
        """Test copy_unfrozen() works on unfrozen configs too."""
        original = SimpleConfig(name="test", value=42)
        copy = original.copy_unfrozen()

        assert not copy.is_frozen()
        copy.name = "changed"
        assert copy.name == "changed"
        assert original.name == "test"  # Original unchanged


class TestNestedFreeze:
    """Test freeze behavior with nested configurations."""

    def test_freeze_nested_config(self):
        """Test that freeze works on parent with nested config."""
        nested = NestedConfig(app_name="myapp", port=8080)
        parent = ParentConfig(environment="prod", service=nested)

        parent.freeze()

        # Parent should be frozen
        with pytest.raises(AttributeError):
            parent.environment = "dev"

        # Note: Nested config freeze propagation depends on implementation
        # This test documents current behavior

    def test_nested_config_independence(self):
        """Test that nested configs can have independent freeze state."""
        nested = NestedConfig(app_name="myapp", port=8080)
        parent = ParentConfig(environment="prod", service=nested)

        # Freeze only parent
        parent.freeze()

        # Parent frozen
        with pytest.raises(AttributeError):
            parent.environment = "dev"

        # Nested is independent (current implementation)
        nested.app_name = "changed"
        assert nested.app_name == "changed"

    def test_copy_unfrozen_with_nested(self):
        """Test copy_unfrozen() with nested configuration."""
        nested = NestedConfig(app_name="myapp", port=8080)
        parent = ParentConfig(environment="prod", service=nested).freeze()

        copy = parent.copy_unfrozen()

        # Copy should be mutable
        assert not copy.is_frozen()
        copy.environment = "dev"
        assert copy.environment == "dev"

        # Original still frozen
        assert parent.is_frozen()
        with pytest.raises(AttributeError):
            parent.environment = "dev"


class TestFreezeMethods:
    """Test freeze-related methods and edge cases."""

    def test_method_chaining(self):
        """Test that freeze methods support method chaining."""
        config = SimpleConfig(name="test", value=42).freeze().unfreeze().freeze()

        assert config.is_frozen()

    def test_freeze_with_dict_operations(self):
        """Test that frozen config still allows dict conversions."""
        config = SimpleConfig(name="test", value=42).freeze()

        # These read-only operations should work
        data = config.to_dict()
        assert data == {"name": "test", "value": 42}

        safe_data = config.to_safe_dict()
        assert safe_data == {"name": "test", "value": 42}

    def test_freeze_with_json_operations(self):
        """Test that frozen config still allows JSON conversions."""
        config = SimpleConfig(name="test", value=42).freeze()

        # Read-only JSON operations should work
        json_str = config.to_json()
        assert "test" in json_str
        assert "42" in json_str

    def test_freeze_does_not_affect_initialization(self):
        """Test that new instances are not affected by frozen instances."""
        config1 = SimpleConfig(name="first", value=1).freeze()
        config2 = SimpleConfig(name="second", value=2)

        # config1 is frozen
        assert config1.is_frozen()
        with pytest.raises(AttributeError):
            config1.name = "changed"

        # config2 is not frozen
        assert not config2.is_frozen()
        config2.name = "changed"
        assert config2.name == "changed"

    def test_freeze_survives_validation(self):
        """Test that freeze state is preserved after validation."""
        config = SimpleConfig(name="test", value=42).freeze()

        # Trigger validation
        assert config.model_validate({"name": "test", "value": 42})

        # Should still be frozen
        assert config.is_frozen()


class TestEdgeCases:
    """Test edge cases and error conditions."""

    def test_freeze_empty_config(self):
        """Test freeze on config with default values."""

        class DefaultConfig(ConfigBase):
            name: str = "default"
            value: int = 0

        config = DefaultConfig().freeze()

        assert config.is_frozen()
        with pytest.raises(AttributeError):
            config.name = "changed"

    def test_freeze_after_modification(self):
        """Test that freeze locks in current state."""
        config = SimpleConfig(name="original", value=1)
        config.name = "modified"
        config.freeze()

        # Should freeze with modified value
        assert config.name == "modified"
        with pytest.raises(AttributeError):
            config.name = "changed_again"

    def test_unfreeze_never_frozen(self):
        """Test that unfreeze on never-frozen config is safe."""
        config = SimpleConfig(name="test", value=42)
        config.unfreeze()  # Should not raise

        assert not config.is_frozen()
        config.name = "changed"
        assert config.name == "changed"

    def test_multiple_instances_independence(self):
        """Test that freeze state is per-instance."""
        config1 = SimpleConfig(name="first", value=1)
        config2 = SimpleConfig(name="second", value=2)

        config1.freeze()

        # config1 frozen, config2 not
        assert config1.is_frozen()
        assert not config2.is_frozen()

        with pytest.raises(AttributeError):
            config1.name = "changed"

        config2.name = "changed"
        assert config2.name == "changed"
