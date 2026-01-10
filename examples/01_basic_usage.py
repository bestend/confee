"""Example 01: Basic confee Usage

This example demonstrates the fundamentals of using confee:
- Loading configuration from YAML files
- Type-safe config access with Pydantic
- Default values and validation
- Basic operations (dict conversion, printing)
"""

from confee import ConfigBase


# Step 1: Define your configuration schema
class DatabaseConfig(ConfigBase):
    """Database connection settings."""

    host: str = "localhost"
    port: int = 5432
    database: str = "myapp"
    username: str = "admin"
    password: str = ""  # Will be overridden from file


class AppConfig(ConfigBase):
    """Main application configuration."""

    name: str
    version: str = "1.0.0"
    debug: bool = False
    workers: int = 4
    database: DatabaseConfig = DatabaseConfig()


# Step 2: Create a sample config file
SAMPLE_CONFIG = """
# app.yaml
name: my-awesome-app
version: 2.1.0
debug: false
workers: 8

database:
  host: prod-db.example.com
  port: 5432
  database: production_db
  username: prod_user
  password: super_secret_password
"""

print("=" * 60)
print("confee Example 01: Basic Usage")
print("=" * 60)
print()

# For demonstration, we'll create the config in memory
# In real usage, you'd load from a file:
# config = AppConfig.load(config_file="app.yaml")

# Step 3: Create config from dictionary (simulating file load)
import yaml

config_data = yaml.safe_load(SAMPLE_CONFIG)
config = AppConfig(**config_data)

# Step 4: Access configuration values (type-safe!)
print("📋 Configuration Loaded:")
print(f"  App Name: {config.name}")
print(f"  Version: {config.version}")
print(f"  Debug Mode: {config.debug}")
print(f"  Workers: {config.workers}")
print()

# Step 5: Access nested configuration
print("🗄️  Database Settings:")
print(f"  Host: {config.database.host}")
print(f"  Port: {config.database.port}")
print(f"  Database: {config.database.database}")
print(f"  Username: {config.database.username}")
# Note: We'll show password masking in example 03
print(f"  Password: {'*' * len(config.database.password)}")
print()

# Step 6: Convert to dictionary
print("📦 Config as Dictionary:")
config_dict = config.to_dict()
print(f"  {config_dict}")
print()

# Step 7: Convert to JSON
print("🔧 Config as JSON:")
config_json = config.to_json(indent=2)
print(config_json)
print()

# Step 8: Demonstrate validation
print("✅ Validation Demo:")
try:
    # This will fail validation (wrong type)
    invalid_config = AppConfig(
        name="test",
        workers="not a number",  # type: ignore
    )
except Exception as e:
    print(f"  ❌ Validation failed as expected: {type(e).__name__}")
    print("     (workers must be an integer)")
print()

# Step 9: Show default values
print("🎯 Default Values:")
minimal_config = AppConfig(name="minimal-app", database=DatabaseConfig())
print(f"  Name: {minimal_config.name}")
print(f"  Version: {minimal_config.version} (default)")
print(f"  Debug: {minimal_config.debug} (default)")
print(f"  Workers: {minimal_config.workers} (default)")
print(f"  Database Host: {minimal_config.database.host} (default)")
print()

# Step 10: Freeze config (immutable)
print("🧊 Freeze Demo:")
config.freeze()
print(f"  Config is frozen: {config.is_frozen()}")
try:
    config.name = "changed"
except AttributeError as e:
    print(f"  ✅ Modification prevented: {e}")
print()

# Unfreeze for demonstration
config.unfreeze()
config.name = "my-awesome-app"  # Restore original

print("=" * 60)
print("✨ Key Takeaways:")
print("  1. Define config schema with ConfigBase + Pydantic")
print("  2. Get IDE autocomplete and type safety")
print("  3. Automatic validation on load")
print("  4. Easy conversion to dict/JSON")
print("  5. Support for nested configurations")
print("  6. Config freezing for immutability")
print("=" * 60)
print()
print("📚 Next: Try 02_cli_overrides.py to learn about CLI args")
